from datetime import datetime
from enum import Enum
from typing import List
from uuid import uuid4

from sqlalchemy import DateTime, Enum as SqlEnum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


class BatchStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Batch(Base):
    __tablename__ = "batches"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4
    )

    exam_name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    uploaded_by: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    pdf_path: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    rubric_path: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    status: Mapped[BatchStatus] = mapped_column(
        SqlEnum(BatchStatus),
        default=BatchStatus.UPLOADED
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    submissions: Mapped[List["Submission"]] = relationship(
        back_populates="batch",
        cascade="all, delete-orphan"
    )