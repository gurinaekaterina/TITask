from pathlib import Path
from typing import Type
from .base import BaseFileHandler
from .handlers import TxtFileHandler, CsvFileHandler, XlsxFileHandler
from .constants import ValidationResult


class FileValidator:
    file_handlers: dict[str, Type[BaseFileHandler]] = {
        ".txt": TxtFileHandler,
        ".csv": CsvFileHandler,
        ".xlsx": XlsxFileHandler,
    }

    @classmethod
    def validate_file(cls, filepath: str) -> ValidationResult:
        handler_class = cls.file_handlers.get(Path(filepath).suffix.lower())
        if handler_class is None:
            return ValidationResult(valid=False, reason="Unsupported file type")
        return handler_class.validate(filepath)
