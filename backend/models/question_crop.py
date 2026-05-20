from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class CropStatus(str, Enum):
    PENDING = "PENDING"
    OCR_COMPLETE = "OCR_COMPLETE"
    GRADED = "GRADED"
    REVIEW_PENDING = "REVIEW_PENDING"
    APPROVED = "APPROVED"
    FAILED = "FAILED"


class QuestionCrop(Base):
    __tablename__ = "question_crops"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    submission_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("submissions.id"),
        nullable=False
    )

    question_id: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    page_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    crop_image_path: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    ocr_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    status: Mapped[CropStatus] = mapped_column(
        SqlEnum(CropStatus),
        default=CropStatus.PENDING
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    grading_result = relationship(
        "GradingResult",
        back_populates="question_crop",
        uselist=False
    )

    submission = relationship("Submission")