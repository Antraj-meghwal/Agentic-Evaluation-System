from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, ForeignKey
from sqlalchemy import Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class ResolutionStatus(str, Enum):
    GRADER_ACCEPTED = "GRADER_ACCEPTED"
    CRITIC_CORRECTED = "CRITIC_CORRECTED"
    REQUIRES_HUMAN = "REQUIRES_HUMAN"


class GradingResult(Base):
    __tablename__ = "grading_results"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    question_crop_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("question_crops.id"),
        nullable=False
    )

    final_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    max_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    confidence_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    resolution_status: Mapped[ResolutionStatus] = mapped_column(
        SqlEnum(ResolutionStatus),
        default=ResolutionStatus.GRADER_ACCEPTED
    )

    requires_human_review: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    grader_output: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )

    critic_output: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )

    coordinator_output: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True
    )

    final_feedback: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    question_crop = relationship(
        "QuestionCrop",
        back_populates="grading_result"
    )

    review_actions = relationship(
        "ReviewAction",
        back_populates="grading_result",
        cascade="all, delete-orphan"
    )