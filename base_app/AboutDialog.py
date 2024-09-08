from PySide6 import QtCore, QtWidgets


class AboutDialog(QtWidgets.QDialog):
    _about_html_template = """
    <p><strong>{app_name} App by Sortition Foundation</strong></p>

    <p>Version: {app_version}</p>

    <p>This software is published under the GNU LESSER GENERAL PUBLIC LICENSE (LGPL) Version 3.</p>

    <p>This software was created by Philipp C. Verpoort while an Associate at the 
    <a href="https://www.sortitionfoundation.org">Sortition Foundation</a>. The initial funding for the development was 
    provided by the <a href="https://www.involve.org.uk/">Involve Foundation</a>.</p>
    """

    def __init__(self, app_name: str, app_version: str, parent = None):
        super(AboutDialog, self).__init__(parent)
        about_html = self._about_html_template.format(app_name=app_name, app_version=app_version)
        self._setup_ui(about_html)

    def _setup_ui(self, about_html):
        self.setFixedSize(400, 300)
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("About Dialog", "About this Software"))
        self.label.setText(about_html)

    @staticmethod
    def display(app_name: str, app_version: str, parent = None):
        dialog = AboutDialog(app_name, app_version, parent)
        dialog.exec_()
