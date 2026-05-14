# FastAPI tools
from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Depends

# SQLAlchemy session
from sqlalchemy.orm import Session

# File handling
import shutil

# DB dependency
from dependencies import get_db

# Database model
from models.upload_model import UploadedFile


# Create router
router = APIRouter()


# -----------------------------------
# Upload file endpoint
# -----------------------------------
@router.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # File storage path
    file_location = f"uploads/{file.filename}"

    # Save file to disk
    with open(file_location, "wb") as buffer:

        shutil.copyfileobj(file.file, buffer)

    # Public URL
    file_url = (
        f"http://127.0.0.1:8000/uploads/{file.filename}"
    )

    # Create DB object
    uploaded_file = UploadedFile(

        filename=file.filename,

        file_url=file_url
    )

    # Insert into DB
    db.add(uploaded_file)

    db.commit()

    db.refresh(uploaded_file)

    # Return response
    return {

        "id": uploaded_file.id,

        "filename": uploaded_file.filename,

        "file_url": uploaded_file.file_url,

        "message": "File uploaded successfully"
    }


# -----------------------------------
# Get all uploaded files
# -----------------------------------
@router.get("/uploads")
def get_uploads(
    db: Session = Depends(get_db)
):

    # Fetch all uploads
    uploads = db.query(UploadedFile).all()

    return uploads