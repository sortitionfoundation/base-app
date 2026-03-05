from PySide6 import QtCore, QtWidgets



ABOUT_HTML_TEMPLATE: str = (
"""
<p><strong>{app_name} App by Sortition Foundation</strong></p>

<p>Version: {app_version}</p>
"""
)


class AboutDialog(QtWidgets.QDialog):
    def __init__(self, app_name: str, app_version: str, about_html_template: str, parent = None):
        super(AboutDialog, self).__init__(parent)
        about_html = about_html_template.format(app_name=app_name, app_version=app_version)
        self._setup_ui(about_html)

    def _setup_ui(self, about_html):
        self.setFixedSize(400, 300)
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        self.text_browser = QtWidgets.QTextBrowser(self)
        self.text_browser.setOpenExternalLinks(True)
        self.text_browser.setHtml(about_html)
        layout.addWidget(self.text_browser)

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("About Dialog", "About this software"))

    @staticmethod
    def display(app_name: str, app_version: str, about_html_template: str | None, parent = None):
        about_html_template = about_html_template or ABOUT_HTML_TEMPLATE
        dialog = AboutDialog(app_name, app_version, about_html_template, parent)
        dialog.exec_()
