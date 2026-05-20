from datetime import datetime
from enum import Enum
from typing import List
from uuid import uuid4

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class SubmissionStatus(str, Enum):
    PENDING = "PENDING"
    CROPPED = "CROPPED"
    GRADED = "GRADED"
    REVIEWED = "REVIEWED"


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    batch_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("batches.id"),
        nullable=False
    )

    student_id: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    original_pdf_path: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    status: Mapped[SubmissionStatus] = mapped_column(
        SqlEnum(SubmissionStatus),
        default=SubmissionStatus.PENDING
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    batch: Mapped["Batch"] = relationship(
        back_populates="submissions"
    )

    question_crops: Mapped[List["QuestionCrop"]] = relationship(
        cascade="all, delete-orphan"
    )