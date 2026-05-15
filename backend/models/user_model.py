# SQLAlchemy tools
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy.orm import relationship
# Import Base
from database import Base


# -----------------------------------
# User table
# -----------------------------------
class User(Base):

    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # User email
    email = Column(
        String,
        unique=True,
        nullable=False
    )

    # Hashed password
    hashed_password = Column(
        String,
        nullable=False
    )

    # User role
    role = Column(
        String,
        nullable=False
    )

    # User uploads relationship
    uploads = relationship(
        "UploadedFile",
        back_populates="owner"
    )


