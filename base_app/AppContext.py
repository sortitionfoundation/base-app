from enum import Enum
from sys import exit

from PySide6 import QtWidgets

from .AbstractProject import AbstractProject
from .AbstractMainWindow import AbstractMainWindow
from .AbstractModelManager import AbstractModelManager
from .ProjectManager import ProjectManager


class AppStatus(Enum):
    CLOSED = 0
    OPENED = 1

class AppChanges(Enum):
    SAVED = 0
    UNSAVED = 1


class AppContext:
    _app_name: str
    _app_version: str
    _project_file_ending: str

    _qapp: QtWidgets.QApplication

    _main_window: AbstractMainWindow
    _model_manager: AbstractModelManager
    _project_manager: ProjectManager

    _status: AppStatus
    _changes: AppChanges

    def __init__(self,
                 app_name: str,
                 app_version: str,
                 project_file_ending: str,
                 main_window_cls: type[AbstractMainWindow],
                 model_manager_cls: type[AbstractModelManager],
                 project_cls: type[AbstractProject],
                 about_html_template: str | None = None,
                 ):
        # Set app status to closed and changes to saved.
        self._status = AppStatus.CLOSED
        self._changes = AppChanges.SAVED

        # Set application name and version.
        self._app_name = app_name
        self._app_version = app_version
        self._project_file_ending = project_file_ending
        self._about_html_template = about_html_template

        # Create QApplication.
        self._qapp = QtWidgets.QApplication()

        # Create project manager, model manager, and main window.
        self._project_manager = ProjectManager(self, project_cls)
        self._model_manager = model_manager_cls(self)
        self._main_window = main_window_cls(self)

    def launch(self):
        return self._qapp.exec()

    # app state methods
    @property
    def status(self) -> AppStatus:
        return self._status

    @status.setter
    def status(self, status: AppStatus):
        if not isinstance(status, AppStatus):
            raise Exception(f"Unknown app status provided: {status}")
        self._status = status

    @property
    def is_open(self) -> bool:
        return self._status == AppStatus.OPENED

    def set_opened(self):
        self._status = AppStatus.OPENED

    def set_closed(self):
        self._status = AppStatus.CLOSED

    @property
    def changes(self) -> AppChanges:
        return self._changes

    @changes.setter
    def changes(self, changes: AppChanges):
        if not isinstance(changes, AppChanges):
            raise Exception(f"Unknown app changes provided: {changes}")
        self._changes = changes

    @property
    def is_saved(self) -> bool:
        return self._changes == AppChanges.SAVED

    def set_unsaved(self):
        self._changes = AppChanges.UNSAVED

    def set_saved(self):
        self._changes = AppChanges.SAVED

    @property
    def app_name(self) -> str:
        return self._app_name

    @property
    def app_version(self) -> str:
        return self._app_version

    @property
    def about_html_template(self) -> str:
        return self._about_html_template

    @property
    def project_file_ending(self) -> str:
        return self._project_file_ending

    ### get interfaces and models as properties
    @property
    def qapp(self) -> QtWidgets.QApplication:
        return self._qapp

    @property
    def main_window(self) -> AbstractMainWindow:
        return self._main_window

    @property
    def model_manager(self) -> AbstractModelManager:
        return self._model_manager

    @property
    def project_manager(self) -> ProjectManager:
        return self._project_manager

    def quit(self):
        exit()
