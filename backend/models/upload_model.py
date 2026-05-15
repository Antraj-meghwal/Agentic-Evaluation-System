# SQLAlchemy tools
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime

# SQLAlchemy relationships
from sqlalchemy.orm import relationship

# Timestamp utilities
from datetime import datetime

# Import Base
from database import Base


# -----------------------------------
# Uploaded files table
# -----------------------------------
class UploadedFile(Base):

    __tablename__ = "uploaded_files"

    # Primary key
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Uploaded filename
    filename = Column(
        String,
        nullable=False
    )

    # Public file URL
    file_url = Column(
        String,
        nullable=False
    )

    # Upload owner
    owner_id = Column(
        Integer,
        ForeignKey("users.id")
    )

    # Processing status
    status = Column(
        String,
        default="uploaded"
    )

    # Upload timestamp
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    # Relationship to user
    owner = relationship(
        "User",
        back_populates="uploads"
    )