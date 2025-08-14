from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from tempfile import NamedTemporaryFile
import shutil
from pathlib import Path
from .file_validator import FileValidator

app = FastAPI()

class ValidationResponse(BaseModel):
    filename: str
    valid: bool

@app.post("/validate-file", response_model=ValidationResponse)
async def validate_file(file: UploadFile = File(...)):
    file_ext = Path(file.filename).suffix.lower()

    if file_ext not in FileValidator.file_handlers:
        return ValidationResponse(filename=file.filename, valid=False)

    with NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_path = temp_file.name

    try:
        is_valid = bool(FileValidator.validate_file(temp_path))
        return ValidationResponse(filename=file.filename, valid=is_valid)
    finally:
        Path(temp_path).unlink(missing_ok=True)
