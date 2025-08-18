from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Iterable

from .constants import TARGET_WORD, ValidationResult


class BaseFileHandler(ABC):
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self._is_file_valid: bool = False
        self._reason: str = ""

    @property
    def target_word_lower(self) -> str:
        return TARGET_WORD.casefold()

    def process(self) -> None:
        stream = self._read()
        result = self._search(stream)
        self._is_file_valid = bool(result.valid)
        self._reason = result.reason

    def is_valid(self) -> bool:
        return bool(self._is_file_valid)

    @property
    def reason(self) -> str:
        return self._reason

    @abstractmethod
    def _read(self) -> Iterable[Any]:
        raise NotImplementedError

    @abstractmethod
    def _search(self, stream: Iterable[Any]) -> ValidationResult:
        raise NotImplementedError
