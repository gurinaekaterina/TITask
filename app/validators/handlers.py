import csv
from typing import Dict, Generator, Iterable, Mapping

import pandas as pd

from .base import BaseFileHandler
from .constants import (
    TARGET_WORD_DISPLAY,
    COMPANY_NAME_COL,
    DEFAULT_TXT_CHUNK,
    ValidationResult,
    normalize_text,
)


def validate_tabular_data(
    rows: Iterable[Mapping[str, str]],
    target_word: str,
) -> ValidationResult:
    if not target_word:
        return ValidationResult(
            valid=False, reason=f"Target word {TARGET_WORD_DISPLAY} is empty"
        )

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
                return ValidationResult(
                    valid=False, reason=f"Missing column '{COMPANY_NAME_COL}'"
                )

        normalized_row: Dict[str, str] = {k: normalize_text(v) for k, v in row.items()}

        for col, val in normalized_row.items():
            if col != company_column and target_word in val:
                return ValidationResult(
                    valid=False,
                    reason=f"Word {TARGET_WORD_DISPLAY} found outside column '{COMPANY_NAME_COL}' — file is invalid",
                )

        if target_word in normalized_row.get(company_column, ""):
            found_in_company = True

    if not has_data_rows:
        return ValidationResult(valid=False, reason="No data rows")

    if found_in_company:
        return ValidationResult(
            valid=True,
            reason=f"Word {TARGET_WORD_DISPLAY} found in column '{COMPANY_NAME_COL}'",
        )

    return ValidationResult(
        valid=False,
        reason=f"Word {TARGET_WORD_DISPLAY} not found in column '{COMPANY_NAME_COL}'",
    )


class TxtFileHandler(BaseFileHandler):
    def __init__(
        self,
        filepath: str,
        chunk_size: int = DEFAULT_TXT_CHUNK,
        encoding: str = "utf-8",
    ):
        super().__init__(filepath)
        self.chunk_size = chunk_size
        self.encoding = encoding

    def _read(self) -> Generator[str, None, None]:
        with open(self.filepath, "r", encoding=self.encoding, errors="ignore") as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                yield chunk

    def _search(self, stream: Iterable[str]) -> ValidationResult:
        target_word = self.target_word_lower
        if not target_word:
            return ValidationResult(
                valid=False, reason=f"Target word {TARGET_WORD_DISPLAY} is empty"
            )

        tail = ""
        overlap = max(len(target_word) - 1, 0)

        for chunk in stream:
            s = (tail + chunk).casefold()
            if target_word in s:
                return ValidationResult(
                    valid=True, reason=f"Word {TARGET_WORD_DISPLAY} found in text"
                )
            tail = s[-overlap:] if overlap else ""

        return ValidationResult(
            valid=False, reason=f"Word {TARGET_WORD_DISPLAY} not found in text"
        )


class CsvFileHandler(BaseFileHandler):
    def __init__(self, filepath: str, encoding: str = "utf-8-sig"):
        super().__init__(filepath)
        self.encoding = encoding

    def _read(self) -> Iterable[dict[str, str]]:
        with open(self.filepath, "r", newline="", encoding=self.encoding, errors="ignore") as f:
            reader = csv.DictReader(f)
            rows: list[dict[str, str]] = []
            for row in reader:
                rows.append({k: ("" if v is None else str(v)) for k, v in row.items()})
            return rows

    def _search(self, stream: Iterable[dict[str, str]]) -> ValidationResult:
        return validate_tabular_data(stream, self.target_word_lower)


class XlsxFileHandler(BaseFileHandler):
    def _read(self) -> Iterable[dict[str, str]]:
        df = pd.read_excel(self.filepath, dtype=str).fillna("")
        return [{k: ("" if v is None else str(v)) for k, v in rec.items()}
                for rec in df.to_dict(orient="records")]

    def _search(self, stream: Iterable[dict[str, str]]) -> ValidationResult:
        return validate_tabular_data(stream, self.target_word_lower)
