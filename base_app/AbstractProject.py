from typing import Callable, ClassVar, Self
from abc import ABC, abstractmethod
from pathlib import Path

from base_app import AbstractMainWindow


class AbstractProject(ABC):
    #: Bumped by a subclass whenever its saved-project data shape changes in
    #: a way that needs a migration to stay readable (a field renamed, added
    #: with no sensible default, restructured, removed and repurposed, etc.).
    #: Starts at 1. See `migrations()` for how upgrades are registered; a
    #: project class that never overrides either stays on version 1 forever,
    #: which is fine as long as its data shape never needs one.
    SCHEMA_VERSION: ClassVar[int] = 1

    _output_dir: None | Path

    def __init__(self, output_dir: None | Path = None):
        self._output_dir = output_dir

    @classmethod
    def new(cls, main_window: AbstractMainWindow) -> Self:
        return cls()

    @classmethod
    def migrations(cls) -> dict[int, Callable[[dict], dict]]:
        """Map `{from_version: migrate}` used to upgrade an older project
        file's raw data up to `SCHEMA_VERSION`, one step at a time, when
        opening it.

        `migrate(data) -> data` receives the project's data as the plain
        dict/list structure `jsonpickle` produces (i.e. *before* it's turned
        back into real objects), so it's free to add/rename/remove/restructure
        keys directly with no dependency on any of the current or past Python
        classes. It receives data at `from_version` and must return the
        equivalent data at `from_version + 1`.

        Register one entry here per version bump, e.g. after bumping
        `SCHEMA_VERSION` from 1 to 2 for a field renamed from `foo` to `bar`::

            @classmethod
            def migrations(cls):
                def _v1_to_v2(data):
                    data['bar'] = data.pop('foo')
                    return data
                return {1: _v1_to_v2}

        The base app chains together whatever steps are needed to reach
        `SCHEMA_VERSION` when opening a file, and raises a clear error if a
        step is missing (e.g. the file is newer than this app understands, or
        a version was skipped without a migration for it).
        """
        return {}

    @property
    def output_dir(self) -> None | Path:
        return self._output_dir

    @output_dir.setter
    def output_dir(self, output_dir: Path):
        self._output_dir = output_dir
