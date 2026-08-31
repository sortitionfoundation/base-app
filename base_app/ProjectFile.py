"""Project-file envelope: compression, app/schema compatibility checks, and
schema migrations, used by `ProjectManager` to read/write `AbstractProject`
files.

A project file is a gzip-compressed JSON envelope::

    {
        "format": "base-app-project",
        "app_id": "<AppContext.app_name of the app that wrote it>",
        "app_version": "<AppContext.app_version of the app that wrote it>",
        "schema_version": <AbstractProject subclass's SCHEMA_VERSION>,
        "data": { ...jsonpickle-encoded project, as plain JSON... },
    }

The envelope lets `decode_project()` reject a file that was never meant for
this app with a clear message (checking `app_id` before ever trying to
reconstruct any objects from `data`), and lets it upgrade `data` through any
migrations registered on the project class (see `AbstractProject.
migrations()`) before finally handing it to jsonpickle.

Files saved before this envelope existed are still read: such a file is just
the bare jsonpickle-encoded project, uncompressed. It's treated as schema
version 1 of whichever project class is opening it (there being no "app_id"/
"schema_version" in it to check against) and migrated up from there like any
other old file.
"""

from __future__ import annotations

import gzip
import json
from typing import TYPE_CHECKING

import jsonpickle

if TYPE_CHECKING:
    from .AbstractProject import AbstractProject


FORMAT_MARKER = 'base-app-project'
LEGACY_SCHEMA_VERSION = 1


class ProjectFileError(Exception):
    """Base class for problems opening a project file, with a message that's
    safe to show to the user as-is."""


class IncompatibleProjectFileError(ProjectFileError):
    """The file is not a project file for this app (or not a project file,
    or not a project of the expected class, at all)."""


class ProjectMigrationError(ProjectFileError):
    """The file needs a migration step that isn't registered, or belongs to a
    schema version newer than this app understands."""


def encode_project(project: 'AbstractProject', app_id: str, app_version: str) -> bytes:
    """Serialise `project` into gzip-compressed project-file bytes."""
    data = json.loads(jsonpickle.encode(project, keys=True))
    envelope = {
        'format': FORMAT_MARKER,
        'app_id': app_id,
        'app_version': app_version,
        'schema_version': type(project).SCHEMA_VERSION,
        'data': data,
    }
    return gzip.compress(json.dumps(envelope).encode('utf-8'))


def decode_project(raw: bytes, project_cls: type['AbstractProject'], app_id: str) -> 'AbstractProject':
    """Reconstruct an `AbstractProject` of type `project_cls` from raw
    project-file bytes, checking compatibility and running any migrations
    needed to bring it up to `project_cls.SCHEMA_VERSION`.

    Raises `ProjectFileError` (or a subclass) for anything that isn't a
    readable, compatible project file; other exceptions indicate an
    unexpected failure while decoding.
    """
    text = _decompress(raw)

    try:
        parsed = json.loads(text)
    except Exception as ex:
        raise IncompatibleProjectFileError(f"This does not look like a project file ({ex}).")

    if isinstance(parsed, dict) and parsed.get('format') == FORMAT_MARKER:
        if parsed.get('app_id') != app_id:
            raise IncompatibleProjectFileError(
                f"This is not a {app_id} project file "
                f"(it belongs to {parsed.get('app_id')!r})."
            )
        schema_version = parsed.get('schema_version', LEGACY_SCHEMA_VERSION)
        data = parsed.get('data')
    else:
        # No envelope: a file saved before this format existed, i.e. the
        # bare jsonpickle-encoded project data. Nothing to check it against,
        # so treat it as schema version 1 and let migrations (if any) and the
        # isinstance check below catch anything actually incompatible.
        schema_version = LEGACY_SCHEMA_VERSION
        data = parsed

    data = _migrate(data, schema_version, project_cls)

    try:
        project = jsonpickle.decode(json.dumps(data), keys=True)
    except Exception as ex:
        raise IncompatibleProjectFileError(f"Could not read project data ({ex}).")

    if not isinstance(project, project_cls):
        raise IncompatibleProjectFileError(f"This is not a valid {app_id} project file.")

    return project


def _decompress(raw: bytes) -> str:
    try:
        return gzip.decompress(raw).decode('utf-8')
    except OSError:
        # Not gzip-compressed -- assume a legacy, plain-text project file.
        return raw.decode('utf-8')


def _migrate(data: dict, schema_version: int, project_cls: type['AbstractProject']) -> dict:
    current_version = project_cls.SCHEMA_VERSION

    if schema_version > current_version:
        raise ProjectMigrationError(
            f"This project file was created with a newer version of the app "
            f"(schema version {schema_version}) than this one supports "
            f"(schema version {current_version}). Please use a newer version "
            f"of the app to open it."
        )

    migrations = project_cls.migrations()
    while schema_version < current_version:
        migrate_step = migrations.get(schema_version)
        if migrate_step is None:
            raise ProjectMigrationError(
                f"Don't know how to upgrade this project file from schema "
                f"version {schema_version} to {schema_version + 1}."
            )
        try:
            data = migrate_step(data)
        except Exception as ex:
            raise ProjectMigrationError(
                f"Upgrading this project file from schema version "
                f"{schema_version} to {schema_version + 1} failed: {ex}"
            )
        schema_version += 1

    return data
