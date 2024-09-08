from typing import Self
from abc import ABC, abstractmethod
from pathlib import Path

from base_app import AbstractMainWindow


class AbstractProject(ABC):
    _output_dir: None | Path

    def __init__(self, output_dir: None | Path = None):
        self._output_dir = output_dir

    @classmethod
    def new(cls, main_window: AbstractMainWindow) -> Self:
        return cls()

    @property
    def output_dir(self) -> None | Path:
        return self._output_dir

    @output_dir.setter
    def output_dir(self, output_dir: Path):
        self._output_dir = output_dir
