import csv
from typing import Any, Dict, Generator, Iterable, Mapping

import pandas as pd

from .base import BaseFileHandler
from .constants import (
    COMPANY_NAME_COL,
    DEFAULT_TXT_CHUNK,
    TARGET_WORD_DISPLAY,
    ValidationResult,
    normalize_text,
)


def normalize_row(row: Mapping[str, Any]) -> dict[str, str]:
    return {k: ("" if v is None else str(v)) for k, v in row.items()}


def validate_tabular_data(
    rows: Iterable[Mapping[str, str]],
    target_word: str,
) -> ValidationResult:
    if not target_word:
        return ValidationResult(False, f"Target word {TARGET_WORD_DISPLAY} is empty")

    company_column: str | None = None
    found_in_company = False
    has_data_rows = False

    for row in rows:
        has_data_rows = True

        if company_column is None:
            normalized_headers = {normalize_text(k): k for k in row.keys()}
            target_column_name = normalize_text(COMPANY_NAME_COL)
            company_column = normalized_headers.get(target_column_name)
            if company_column is None:
                return ValidationResult(False, f"Missing column '{COMPANY_NAME_COL}'")

        normalized_row: Dict[str, str] = {k: normalize_text(v) for k, v in row.items()}

        for col, val in normalized_row.items():
            if col != company_column and target_word in val:
                return ValidationResult(
                    False,
                    f"Word {TARGET_WORD_DISPLAY} found outside column '{COMPANY_NAME_COL}' — file is invalid",
                )

        if target_word in normalized_row.get(company_column, ""):
            found_in_company = True

    if not has_data_rows:
        return ValidationResult(False, "No data rows")

    if found_in_company:
        return ValidationResult(
            True, f"Word {TARGET_WORD_DISPLAY} found in column '{COMPANY_NAME_COL}'"
        )

    return ValidationResult(
        False, f"Word {TARGET_WORD_DISPLAY} not found in column '{COMPANY_NAME_COL}'"
    )


class TxtFileHandler(BaseFileHandler):
    @classmethod
    def _read(
        cls, filepath: str, *, chunk_size: int, encoding: str
    ) -> Generator[str, None, None]:
        with open(filepath, "r", encoding=encoding, errors="ignore") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    @classmethod
    def validate(cls, filepath: str, **kwargs: Any) -> ValidationResult:
        chunk_size = int(kwargs.get("chunk_size", DEFAULT_TXT_CHUNK))
        encoding = str(kwargs.get("encoding", "utf-8"))

        target_word = cls.target_word_lower()
        if not target_word:
            return ValidationResult(
                False, f"Target word {TARGET_WORD_DISPLAY} is empty"
            )

        tail = ""
        overlap = max(len(target_word) - 1, 0)

        for chunk in cls._read(filepath, chunk_size=chunk_size, encoding=encoding):
            s = (tail + chunk).casefold()
            if target_word in s:
                return ValidationResult(
                    True, f"Word {TARGET_WORD_DISPLAY} found in text"
                )
            tail = s[-overlap:] if overlap else ""

        return ValidationResult(False, f"Word {TARGET_WORD_DISPLAY} not found in text")


class CsvFileHandler(BaseFileHandler):
    @classmethod
    def validate(cls, filepath: str, **kwargs: Any) -> ValidationResult:
        encoding = str(kwargs.get("encoding", "utf-8-sig"))

        with open(filepath, "r", newline="", encoding=encoding, errors="ignore") as f:
            reader = csv.DictReader(f)
            rows = [normalize_row(row) for row in reader]
        return validate_tabular_data(rows, cls.target_word_lower())


class XlsxFileHandler(BaseFileHandler):
    @classmethod
    def validate(cls, filepath: str, **kwargs: Any) -> ValidationResult:
        df = pd.read_excel(filepath, dtype=str).fillna("")
        rows = [normalize_row(rec) for rec in df.to_dict(orient="records")]
        return validate_tabular_data(rows, cls.target_word_lower())
