import os

from app.validators.constants import COMPANY_NAME_COL
from app.validators.file_validator import FileValidator


def test_txt_150mb_streaming_valid(uploads_dir):
    path = os.path.join(uploads_dir, "random_text_80mb.txt")
    assert os.path.exists(path), f"Missing file: {path}"
    res = FileValidator.validate_file(path)
    assert res.valid is True
    assert "found in text" in res.reason


def test_csv_valid_only_in_company_name(uploads_dir):
    path = os.path.join(uploads_dir, "valid.csv")
    assert os.path.exists(path)
    res = FileValidator.validate_file(path)
    assert res.valid is True
    assert COMPANY_NAME_COL in res.reason


def test_csv_invalid_word_outside_company(uploads_dir):
    path = os.path.join(uploads_dir, "invalid.csv")
    assert os.path.exists(path)
    res = FileValidator.validate_file(path)
    assert res.valid is False
    assert "outside column" in res.reason


def test_xlsx_valid_only_in_company_name(uploads_dir):
    path = os.path.join(uploads_dir, "valid.xlsx")
    assert os.path.exists(path)
    res = FileValidator.validate_file(path)
    assert res.valid is True
    assert COMPANY_NAME_COL in res.reason


def test_xlsx_invalid_outside_company(uploads_dir):
    path = os.path.join(uploads_dir, "invalid.xlsx")
    assert os.path.exists(path)
    res = FileValidator.validate_file(path)
    assert res.valid is False
    assert "outside column" in res.reason
