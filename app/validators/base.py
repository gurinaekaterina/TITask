from abc import ABC, abstractmethod
from typing import Any
from .constants import TARGET_WORD, ValidationResult


class BaseFileHandler(ABC):
    @classmethod
    def target_word_lower(cls) -> str:
        return TARGET_WORD.casefold()

    @classmethod
    @abstractmethod
    def validate(cls, filepath: str, **kwargs: Any) -> ValidationResult:
        raise NotImplementedError
