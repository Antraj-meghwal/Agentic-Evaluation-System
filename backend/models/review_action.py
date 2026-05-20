from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey
from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class ReviewActionType(str, Enum):
    APPROVED = "APPROVED"
    OVERRIDDEN = "OVERRIDDEN"
    FLAGGED = "FLAGGED"


class ReviewAction(Base):
    __tablename__ = "review_actions"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    grading_result_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("grading_results.id"),
        nullable=False
    )

    reviewer_id: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    action_type: Mapped[ReviewActionType] = mapped_column(
        SqlEnum(ReviewActionType),
        nullable=False
    )

    original_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    updated_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    review_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    grading_result = relationship(
        "GradingResult",
        back_populates="review_actions"
    )