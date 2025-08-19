from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserPublic


class CommentCreateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10_000)


class CommentUpdateRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10_000)


class CommentResponse(BaseModel):
    id: int
    text: str
    user_id: int
    file_id: int
    created_at: datetime
    updated_at: datetime
    author: UserPublic
    model_config = ConfigDict(from_attributes=True)
