from base_app.AbstractProject import AbstractProject


class AbstractProjectModel:
    _project: None | AbstractProject = None

    def updated_project(self, project: AbstractProject):
        self._project = project
