import csv
import pandas as pd
import numpy as np
from pathlib import Path


class BaseFileHandler:
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.is_file_valid = False
        self.target_word = "Quantori"

    @property
    def target_word_lower(self) -> str:
        return self.target_word.lower()

    def process(self):
        raise NotImplementedError

    def is_valid(self) -> bool:
        return bool(self.is_file_valid)


class TxtFileHandler(BaseFileHandler):
    def process(self):
        chunk_size = 1024 * 1024
        with open(self.filepath, "r") as file:
            while True:
                chunk  = file.read(chunk_size)
                if not chunk :
                    break
                if self.target_word_lower in chunk .lower():
                    self.is_file_valid = True
                    return
        self.is_file_valid = False


class CsvFileHandler(BaseFileHandler):
    def process(self):
        matches_in_company = 0
        with open(self.filepath, "r", newline="") as file:
            csv_reader = csv.DictReader(file)

            for row in csv_reader:
                normalized_row = {k: (v or "").lower() for k, v in row.items()}
                found_in_company = self.target_word_lower in normalized_row.get("Company Name", "")
                found_in_other_cols = any(
                    self.target_word_lower in val
                    for col, val in normalized_row.items()
                    if col != "Company Name"
                )

                if found_in_other_cols:
                    self.is_file_valid = False
                    return

                if found_in_company:
                    matches_in_company += 1

        self.is_file_valid = matches_in_company > 0


class XlsxFileHandler(BaseFileHandler):
    def process(self):
        df = pd.read_excel(self.filepath, dtype=str).fillna("")
        if "Company Name" not in df.columns:
            self.is_file_valid = False
            return

        other_cols = [col for col in df.columns if col != "Company Name"]
        if other_cols:
            other_data = df[other_cols].astype(str).to_numpy(dtype=str)
            other_lower = np.char.lower(other_data)
            if np.any(np.char.find(other_lower, self.target_word_lower) >= 0):
                self.is_file_valid = False
                return

        company_col_lower = df["Company Name"].astype(str).str.lower()
        matches_in_company = company_col_lower.str.contains(self.target_word_lower).sum()
        self.is_file_valid = matches_in_company > 0


class FileValidator:
    file_handlers = {
        ".txt": TxtFileHandler,
        ".csv": CsvFileHandler,
        ".xlsx": XlsxFileHandler,
    }

    @classmethod
    def validate_file(cls, filepath: str) -> bool:
        extension = Path(filepath).suffix.lower()
        handler_class = cls.file_handlers.get(extension)
        handler_instance = handler_class(filepath)
        handler_instance.process()
        return handler_instance.is_valid()
