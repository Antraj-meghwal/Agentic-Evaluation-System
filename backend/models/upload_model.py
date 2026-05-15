# SQLAlchemy column types
from sqlalchemy import Column, Integer, String

# Import Base class
from database import Base


# Uploaded files table
class UploadedFile(Base):

    # Table name
    __tablename__ = "uploaded_files"

    # Columns
    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String, nullable=False)

    file_url = Column(String, nullable=False)
    