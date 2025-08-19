from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.validators.file_validator import FileExtension


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)

    files = relationship("FileUpload", back_populates="uploader", cascade="all,delete")
    comments = relationship("Comment", back_populates="author", cascade="all,delete")


class FileUpload(Base):
    __tablename__ = "files"
    id = Column(Integer, primary_key=True)
    filename = Column(String(512), nullable=False)
    file_type = Column(SqlEnum(FileExtension, name="file_extension"), nullable=False)
    valid = Column(Boolean, nullable=False, default=False)
    reason = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=utcnow, nullable=False)

    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploader = relationship("User", back_populates="files")

    comments = relationship(
        "Comment",
        back_populates="file",
        cascade="all,delete",
        order_by=lambda: Comment.created_at.asc(),
    )


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow, nullable=False)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)

    author = relationship("User", back_populates="comments")
    file = relationship("FileUpload", back_populates="comments")
