from typing import TYPE_CHECKING, Optional

from pathlib import Path

import jsonpickle
from PySide6.QtWidgets import QMessageBox, QFileDialog

from .AbstractProject import AbstractProject

if TYPE_CHECKING:
    from . import AppContext


class ProjectManager:
    _ctx: 'AppContext'

    _project_cls: type[AbstractProject]
    _project: None | AbstractProject = None

    _file_path: None | Path = None
    _project_file_ending: str
    _project_file_format: str

    # constructor
    def __init__(self, ctx: 'AppContext', project_cls: type[AbstractProject]):
        self._ctx = ctx
        self._project_cls = project_cls

        self._project_file_ending = self._ctx.project_file_ending
        self._project_file_format = f"{self._ctx.app_name} project files (*{self._project_file_ending})"

    # properties
    @property
    def file_path(self) -> Path:
        return self._file_path

    @file_path.setter
    def file_path(self, file_path: Path):
        self._file_path = file_path

    def has_file_path(self) -> bool:
        return self._file_path is not None

    @property
    def project(self) -> AbstractProject:
        return self._project

    # reading and writing of project file
    def read_path(self, file_path: Path):
        self.file_path = file_path
        return self._read()

    def _read(self) -> AbstractProject:
        if self._file_path is None:
            raise Exception('Filename is not set.')
        if not (self._file_path.exists() and self._file_path.is_file()):
            raise Exception('File could not be found.')

        try:
            with open(self._file_path, 'r') as file_handle:
                return jsonpickle.decode(file_handle.read(), keys=True)
        except Exception as ex:
            raise Exception(f"Error reading file: {ex}")

    def write_path(self, project: AbstractProject, file_path: Path):
        if file_path is not None:
            self.file_path = file_path
        return self._write(project)

    def _write(self, project: AbstractProject) -> int:
        if self._file_path is None:
            raise Exception('Filename is not set.')

        try:
            with open(self._file_path, 'w') as file_handle:
                return file_handle.write(jsonpickle.encode(project, keys=True))
        except Exception as ex:
            raise Exception(f"Error writing file: {ex}")

    def project_new(self, new_project: Optional[AbstractProject]):
        self._project = new_project
        self._ctx.model_manager.updated_project(self._project)
        self._ctx.set_opened()
        self._ctx.set_unsaved()
        self._ctx.main_window.update_window_title()
        self._ctx.main_window.update_project_status()

    def project_open(self, project_path: Path):
        project = self.read_path(project_path)
        if not isinstance(project, self._project_cls):
            raise Exception('Project is not compatible!')
        self._project = project
        self._ctx.set_opened()
        self._ctx.set_saved()
        self._ctx.model_manager.updated_project(self._project)
        self._ctx.main_window.update_window_title()
        self._ctx.main_window.update_project_status()

    def project_save(self, project_path: Path):
        self.write_path(self._project, project_path)
        self._ctx.set_saved()
        self._ctx.main_window.update_window_title()

    def project_close(self):
        self._project = None
        self._file_path = None
        self._ctx.model_manager.updated_project(None)
        self._ctx.set_closed()
        self._ctx.set_saved()
        self._ctx.main_window.update_window_title()
        self._ctx.main_window.update_project_status()

    def get_output_dir(self) -> None | Path:
        return self._project.output_dir

    def set_output_dir(self, output_dir: Path):
        self._project.output_dir = output_dir

    # project action handling
    def _action_confirm(self):
        if not self._ctx.is_saved:
            reply = QMessageBox.question(
                self._ctx.main_window,
                'Unsaved changes',
                'Would you like to discard your unsaved changes?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                return True
            else:
                return False
        else:
            return True

    def action_project_new(self):
        if self._action_confirm():
            new_project = self._project_cls.new(self._ctx.main_window)
            self.project_new(new_project)

    def action_project_open(self):
        if self._action_confirm():
            project_path, _ = QFileDialog.getOpenFileName(
                self._ctx.main_window,
                'Open project',
                None,
                self._project_file_format,
            )
            if not project_path:
                return
            project_path = Path(project_path)

            try:
                self.project_open(project_path)
            except Exception as ex:
                QMessageBox.critical(
                    self._ctx.main_window,
                    'Error',
                    f"Error while read project file: {ex}",
                )

    def action_project_save(self):
        self._action_project_save(update_path=False)

    def action_project_saveas(self):
        self._action_project_save(update_path=True)

    def _action_project_save(self, update_path: bool = True):
        if not self._ctx.is_open:
            return

        if update_path or not self._ctx.project_manager.has_file_path():
            project_path, scheme = QFileDialog.getSaveFileName(
                self._ctx.main_window,
                'Save project',
                None,
                self._project_file_format,
            )
            if not project_path:
                return
            if not project_path.endswith(self._project_file_ending):
                project_path += self._project_file_ending
            project_path = Path(project_path)
        else:
            project_path = None

        try:
            self.project_save(project_path)
        except Exception as ex:
            QMessageBox.critical(
                self._ctx.main_window,
                'Error',
                f"Error while writing project file: {ex}",
            )

    def action_project_close(self):
        if not self._ctx.is_open:
            return
        if self._action_confirm():
            self.project_close()

    def action_project_output_directory(self):
        old_dir_path = self._ctx.project_manager.get_output_dir()
        dir_path = QFileDialog.getExistingDirectory(
            parent=self._ctx.main_window,
            caption='Define output directory',
            dir=str(old_dir_path) if old_dir_path is not None else None,
        )
        if not dir_path:
            return
        dir_path = Path(dir_path)
        if not (dir_path.exists() and dir_path.is_dir()):
            QMessageBox.critical(
                parent=self._ctx.main_window,
                title='Output directory does not exist',
                text=f"The output directory provided could not be found:\n\n{dir_path}")
            return
        self._ctx.project_manager.set_output_dir(dir_path)
        self._ctx.set_unsaved()

    def action_quit(self):
        if self._action_confirm():
            self._ctx.quit()
