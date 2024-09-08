from typing import TYPE_CHECKING

from abc import ABC, abstractmethod

from .AbstractProject import AbstractProject
from .AbstractProjectModel import AbstractProjectModel

if TYPE_CHECKING:
    from AppContext import AppContext


class AbstractModelManager(ABC):
    _models: dict[str, AbstractProjectModel]

    def __init__(self, ctx: 'AppContext'):
        self._ctx = ctx
        self._models = self._setup_models()

    def __getitem__(self, item):
        return self._models[item]

    @abstractmethod
    def _setup_models(self) -> dict[str, AbstractProjectModel]:
        pass

    def updated_project(self, project: None | AbstractProject):
        for model in self._models.values():
            model.updated_project(project)
