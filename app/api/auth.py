from typing import Annotated

from app.core.security import (
    create_access_token,
    get_db,
    verify_password,
)
from app.db.models import User
from app.schemas.auth import AuthToken, LoginRequest
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=AuthToken)
def login(
    payload: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
):
    stmt = select(User).where(User.email == payload.email)
    user = db.execute(stmt).scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    return AuthToken(
        access_token=create_access_token(sub=user.email), token_type="bearer"
    )
