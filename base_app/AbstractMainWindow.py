from abc import abstractmethod
from typing import TYPE_CHECKING

from PySide6.QtGui import QAction, QDesktopServices
from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QWidget, QLabel, QStackedLayout
from PySide6.QtCore import QUrl

from .AboutDialog import AboutDialog

if TYPE_CHECKING:
    from base_app.AppContext import AppContext


class AbstractMainWindow(QtWidgets.QMainWindow):
    _menu_dict: dict[str, dict]

    def __init__(self, ctx: 'AppContext'):
        # super constructor
        super(AbstractMainWindow, self).__init__(parent=None)

        # set app context
        self._ctx: 'AppContext' = ctx

        # create main menu and attach triggers
        self._create_menu()

        # create UI
        self._create_ui()

        # setup window
        self._window_styling()

        # set window title and project status
        self.update_window_title()
        self.update_project_status()

    def _define_menu(self) -> dict[str, dict]:
        return {
            'project': {
                'name': 'Project',
                'items': {
                    'new': {
                        'type': 'action',
                        'name': '&New',
                        'shortcut': 'Ctrl+N',
                        'desc': 'Create new project',
                        'show_when_closed': True,
                        'trigger': self._ctx.project_manager.action_project_new,
                    },
                    'open': {
                        'type': 'action',
                        'name': '&Open',
                        'shortcut': 'Ctrl+O',
                        'desc': 'Open existing project',
                        'show_when_closed': True,
                        'trigger': self._ctx.project_manager.action_project_open,
                    },
                    'sep1': {
                        'type': 'separator',
                    },
                    'save': {
                        'type': 'action',
                        'name': '&Save',
                        'shortcut': 'Ctrl+S',
                        'desc': 'Save project',
                        'show_when_closed': False,
                        'trigger': self._ctx.project_manager.action_project_save,
                    },
                    'saveas': {
                        'type': 'action',
                        'name': '&Save As',
                        'shortcut': 'Ctrl+Shift+S',
                        'desc': 'Save project as',
                        'show_when_closed': False,
                        'trigger': self._ctx.project_manager.action_project_saveas,
                    },
                    'sep2': {
                        'type': 'separator',
                    },
                    'output-directory': {
                        'type': 'action',
                        'name': 'Set &output directory',
                        'desc': 'Set an output directory for this project.',
                        'show_when_closed': False,
                        'trigger': self._ctx.project_manager.action_project_output_directory,
                    },
                    'sep3': {
                        'type': 'separator',
                    },
                    'close': {
                        'type': 'action',
                        'name': '&Close',
                        'shortcut': 'Ctrl+W',
                        'desc': 'Close project',
                        'show_when_closed': False,
                        'trigger': self._ctx.project_manager.action_project_close,
                    },
                    'quit': {
                        'type': 'action',
                        'name': '&Quit',
                        'shortcut': 'Ctrl+Q',
                        'desc': 'Quit application',
                        'show_when_closed': True,
                        'trigger': self._ctx.project_manager.action_quit,
                    },
                },
            },
            'help': {
                'name': 'Help',
                'items': {
                    'about': {
                        'type': 'action',
                        'name': '&About',
                        'desc': 'Details about this software.',
                        'show_when_closed': True,
                        'trigger': self._action_about,
                    },
                },
            },
        }

    def _create_menu(self):
        menu_bar = self.menuBar()

        self._menus = {}
        self._menu_items: dict[str, QAction] = {}

        # add menu items from dict
        for menu_id, menu_specs in self._define_menu().items():
            menu = menu_bar.addMenu(menu_specs['name'])

            for item_id, item_specs in menu_specs['items'].items():
                match item_specs['type']:
                    case 'action':
                        item = QAction(item_specs['name'], self)
                        if 'shortcut' in item_specs: item.setShortcut(item_specs['shortcut'])
                        if 'desc' in item_specs: item.setStatusTip(item_specs['desc'])
                        if 'checkable' in item_specs: item.setCheckable(item_specs['checkable'])
                        if 'checked' in item_specs: item.setChecked(item_specs['checked'])
                        if 'trigger' in item_specs: item.triggered.connect(item_specs['trigger'])
                        menu.addAction(item)
                        self._menu_items[f"{menu_id}:{item_id}"] = item
                    case 'separator':
                        menu.addSeparator()
                    case _:
                        raise Exception(f"Unknown menu item: {item_id}")

            self._menus[menu_id] = menu

    @abstractmethod
    def _create_main_widget(self) -> QWidget:
        pass

    def _create_ui(self):
        # create main widget (displaying project when it is open)
        self._main_widget = self._create_main_widget()

        # create label (for when project is closed)
        label = QLabel('Create a new project or open an existing one.')
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        stacked_widget = QWidget()

        # create layout
        self.stacked_layout = QStackedLayout()
        self.stacked_layout.addWidget(label)
        self.stacked_layout.addWidget(self._main_widget)
        stacked_widget.setLayout(self.stacked_layout)
        self.setCentralWidget(stacked_widget)

    def _window_styling(self):
        app = self._ctx.qapp

        # set style
        #app.setStyle(QStyleFactory.create('Fusion'))
        self.originalPalette = app.palette()

        size = app.primaryScreen().size()
        height = size.height()
        width = size.width()
        self.setGeometry(int(.1*width), int(.1*height), int(.8*width), int(.8*height))
        self.showMaximized()

    def update_window_title(self):
        if self._ctx.is_open:
            if self._ctx.project_manager.has_file_path():
                project_file_name = self._ctx.project_manager.file_path.name
                if not self._ctx.is_saved:
                    project_file_name += '*'
            else:
                project_file_name = 'Unsaved Project*'
            new_title = f"{project_file_name} — {self._ctx.app_name}"
        else:
            new_title = self._ctx.app_name
        self.setWindowTitle(new_title)

    def update_project_status(self):
        self.stacked_layout.setCurrentIndex(self._ctx.status.value)

        for menu_id, menu_specs in self._define_menu().items():
            self._menus[menu_id].setDisabled(
                not self._ctx.is_open and
                all(not item_specs['show_when_closed']
                for item_specs in menu_specs['items'].values()
                if item_specs['type'] == 'action')
            )

            for item_id, item_specs in menu_specs['items'].items():
                if item_specs['type'] == 'action' and not item_specs['show_when_closed']:
                    self._menu_items[f"{menu_id}:{item_id}"].setDisabled(not self._ctx.is_open)

    def _action_about(self):
        AboutDialog.display(self._ctx.app_name, self._ctx.app_version, self._ctx.about_html_template, self)
