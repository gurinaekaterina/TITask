from dataclasses import dataclass

from app.core.config import settings

TARGET_WORD: str = settings.target_word
TARGET_WORD_DISPLAY: str = f"'{TARGET_WORD}'"
COMPANY_NAME_COL: str = settings.company_name_col
DEFAULT_TXT_CHUNK: int = settings.default_txt_chunk


@dataclass(slots=True)
class ValidationResult:
    valid: bool
    reason: str


def normalize_text(s: str) -> str:
    return ("" if s is None else str(s)).strip().casefold()
