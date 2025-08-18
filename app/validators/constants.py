from dataclasses import dataclass

TARGET_WORD: str = "Quantori"
TARGET_WORD_DISPLAY: str = f"'{TARGET_WORD}'"
COMPANY_NAME_COL: str = "Company Name"
DEFAULT_TXT_CHUNK: int = 1024 * 1024


@dataclass(slots=True)
class ValidationResult:
    valid: bool
    reason: str


def normalize_text(s: str) -> str:
    return ("" if s is None else str(s)).strip().casefold()
