from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.comment import CommentResponse
from app.schemas.user import UserPublic


class FileResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    valid: bool
    reason: str
    created_at: datetime
    uploader_id: int
    uploader: UserPublic
    comments: list["CommentResponse"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
