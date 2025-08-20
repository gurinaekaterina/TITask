from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_current_user, get_db
from app.db.models import Comment, FileUpload, User
from app.schemas.comment import (
    CommentCreateRequest,
    CommentResponse,
    CommentUpdateRequest,
)

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post(
    "/file/{file_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    file_id: int,
    payload: CommentCreateRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    file = db.get(FileUpload, file_id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    comment = Comment(text=payload.text, user_id=user.id, file_id=file.id)
    db.add(comment)
    db.flush()
    stmt = (
        select(Comment)
        .options(joinedload(Comment.author))
        .where(Comment.id == comment.id)
    )
    result = db.execute(stmt).scalar_one()
    db.commit()
    return result


@router.get("/file/{file_id}", response_model=list[CommentResponse])
def get_comments(
    file_id: int,
    db: Annotated[Session, Depends(get_db)],
):
    file = db.get(FileUpload, file_id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )

    stmt = (
        select(Comment)
        .options(joinedload(Comment.author))
        .where(Comment.file_id == file_id)
        .order_by(Comment.created_at.asc())
    )
    comments = db.execute(stmt).scalars().all()
    return comments


@router.patch("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    payload: CommentUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    if comment.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can edit only your comments",
        )

    comment.text = payload.text
    comment.updated_at = datetime.utcnow()
    db.flush()

    stmt = (
        select(Comment)
        .options(joinedload(Comment.author))
        .where(Comment.id == comment.id)
    )
    updated = db.execute(stmt).scalar_one()
    db.commit()
    return updated
