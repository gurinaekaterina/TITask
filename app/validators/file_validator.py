from pathlib import Path
from typing import Type

from app.validators.base import BaseFileHandler
from app.validators.constants import ValidationResult
from app.validators.handlers import TxtFileHandler, CsvFileHandler, XlsxFileHandler


class FileValidator:
    file_handlers: dict[str, Type[BaseFileHandler]] = {
        ".txt": TxtFileHandler,
        ".csv": CsvFileHandler,
        ".xlsx": XlsxFileHandler,
    }

    @classmethod
    def validate_file(cls, filepath: str) -> ValidationResult:
        try:
            handler_class = cls.file_handlers[Path(filepath).suffix.lower()]
        except KeyError:
            return ValidationResult(valid=False, reason="Unsupported file type")
        handler_instance = handler_class(filepath)
        handler_instance.process()
        return ValidationResult(
            valid=handler_instance.is_valid(), reason=handler_instance.reason
        )
