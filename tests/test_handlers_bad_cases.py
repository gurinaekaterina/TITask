import csv
import io
from pathlib import Path

import pandas as pd

from app.validators.constants import COMPANY_NAME_COL, TARGET_WORD
from app.validators.file_validator import FileValidator


def write_csv(
    tmp_path: Path, rows: list[dict[str, str]], headers=("User", "Company Name", "Age")
) -> str:
    p = tmp_path / "tmp.csv"

    sio = io.StringIO(newline="")
    writer = csv.DictWriter(sio, fieldnames=list(headers))
    writer.writeheader()
    writer.writerows(rows)
    p.write_text(sio.getvalue(), encoding="utf-8")
    return str(p)


def test_csv_missing_company_column(tmp_path):
    p = tmp_path / "no_company.csv"
    with p.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["User", "Age"])
        writer.writeheader()
        writer.writerow({"User": "u1", "Age": "10"})
    res = FileValidator.validate_file(str(p))
    assert res.valid is False
    assert "Missing column" in res.reason


def test_csv_zero_occurrences_in_company(tmp_path):
    p = write_csv(
        tmp_path,
        rows=[
            {"User": "John", "Company Name": "Google", "Age": "20"},
            {"User": "Jane", "Company Name": "Amazon", "Age": "21"},
        ],
    )
    res = FileValidator.validate_file(p)
    assert res.valid is False
    assert f"not found in column '{COMPANY_NAME_COL}'" in res.reason


def test_csv_found_outside_company_is_invalid(tmp_path):
    word = TARGET_WORD
    p = write_csv(
        tmp_path,
        rows=[
            {"User": word, "Company Name": "TikTok", "Age": "30"},
        ],
    )
    res = FileValidator.validate_file(p)
    assert res.valid is False
    assert "outside column" in res.reason


def test_csv_valid_found_in_company_only(tmp_path):
    word = TARGET_WORD
    p = write_csv(
        tmp_path,
        rows=[
            {"User": "Ivan", "Company Name": f"My {word} Corp", "Age": "30"},
            {"User": "Vanya", "Company Name": "Other", "Age": "31"},
        ],
    )
    res = FileValidator.validate_file(p)
    assert res.valid is True
    assert f"found in column '{COMPANY_NAME_COL}'" in res.reason


def test_xlsx_zero_occurrences_in_company(tmp_path):
    df = pd.DataFrame([{"User": "Stelyana", "Company Name": "Duolingo", "Age": 10}])
    p = tmp_path / "tmp.xlsx"
    df.to_excel(p, index=False)
    res = FileValidator.validate_file(str(p))
    assert res.valid is False
    assert f"not found in column '{COMPANY_NAME_COL}'" in res.reason


def test_txt_streaming_overlap_at_chunk_boundary(tmp_path):
    word = TARGET_WORD
    content = "x" * 10 + word[: len(word) - 1]
    content += word[-1] + "y" * 10
    p = tmp_path / "tmp.txt"
    p.write_text(content, encoding="utf-8")

    from app.validators import handlers

    res = handlers.TxtFileHandler.validate(str(p), chunk_size=8, encoding="utf-8")
    assert res.valid is True
    assert "found in text" in res.reason
