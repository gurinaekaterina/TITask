import logging
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.core.security import get_current_user, get_db
from app.db.models import Comment, FileUpload, User
from app.schemas.file import FileResponse
from app.validators.file_validator import FileValidator

router = APIRouter(prefix="/files", tags=["files"])

logger = logging.getLogger(__name__)


def get_file_with_comments(db: Session, file_id: int) -> FileUpload | None:
    statement = (
        select(FileUpload)
        .options(
            joinedload(FileUpload.uploader),
            selectinload(FileUpload.comments).joinedload(Comment.author),
        )
        .where(FileUpload.id == file_id)
    )
    return db.execute(statement).scalar_one_or_none()


@router.post(
    "/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED
)
async def upload_file(
    file: Annotated[UploadFile, File(...)],
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Filename is required"
        )

    extension = Path(file.filename).suffix.lower()
    if extension not in FileValidator.file_handlers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type"
        )

    with NamedTemporaryFile(delete=False, suffix=extension) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        result = FileValidator.validate_file(tmp_path)
    except Exception as e:
        logger.error("Validation error for file %s: %s", file.filename, str(e))
        raise HTTPException(status_code=500, detail="Failed to validate file") from e
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    rec = FileUpload(
        filename=file.filename,
        file_type=extension,
        valid=result.valid,
        reason=result.reason,
        uploader_id=user.id,
    )
    db.add(rec)
    db.commit()

    created = get_file_with_comments(db, rec.id)
    return created


@router.get("", response_model=list[FileResponse])
def list_files(db: Annotated[Session, Depends(get_db)]):
    statement = (
        select(FileUpload)
        .options(
            joinedload(FileUpload.uploader),
            selectinload(FileUpload.comments).joinedload(Comment.author),
        )
        .order_by(FileUpload.created_at.desc())
    )
    files = db.execute(statement).scalars().all()
    return files
