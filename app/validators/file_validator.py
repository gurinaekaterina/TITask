from enum import Enum
from pathlib import Path
from typing import Type

from .base import BaseFileHandler
from .constants import ValidationResult
from .handlers import CsvFileHandler, TxtFileHandler, XlsxFileHandler


class FileExtension(str, Enum):
    TXT = ".txt"
    CSV = ".csv"
    XLSX = ".xlsx"


class FileValidator:
    file_handlers: dict[FileExtension, Type[BaseFileHandler]] = {
        FileExtension.TXT: TxtFileHandler,
        FileExtension.CSV: CsvFileHandler,
        FileExtension.XLSX: XlsxFileHandler,
    }

    @classmethod
    def validate_file(cls, filepath: str) -> ValidationResult:
        ext = Path(filepath).suffix.lower()
        try:
            file_ext = FileExtension(ext)
        except ValueError:
            return ValidationResult(valid=False, reason="Unsupported file type")

        handler_class = cls.file_handlers[file_ext]
        return handler_class.validate(filepath)
