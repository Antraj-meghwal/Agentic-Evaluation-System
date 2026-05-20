# -----------------------------------
# Python utilities
# -----------------------------------
import os
import shutil

from datetime import datetime


# -----------------------------------
# FastAPI tools
# -----------------------------------
from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Depends
from fastapi import HTTPException


# -----------------------------------
# SQLAlchemy session
# -----------------------------------
from sqlalchemy.orm import Session


# -----------------------------------
# Dependencies
# -----------------------------------
from core.constants import GRADING_ROLES
from dependencies import (
    get_db,
    get_current_user,
    require_role
)


# -----------------------------------
# Database model
# -----------------------------------
from models.upload_model import UploadedFile


# -----------------------------------
# Response schemas
# -----------------------------------
from schemas.upload_schema import (
    UploadResponse
)


# -----------------------------------
# Allowed file types
# -----------------------------------
ALLOWED_EXTENSIONS = {

    ".pdf",

    ".png",

    ".jpg",

    ".jpeg"
}


# -----------------------------------
# Maximum file size
# 5 MB
# -----------------------------------
MAX_FILE_SIZE = 5 * 1024 * 1024


# -----------------------------------
# Create router
# -----------------------------------
router = APIRouter()


# -----------------------------------
# Upload file endpoint
# -----------------------------------
@router.post(
    "/upload",
    response_model=UploadResponse
)
def upload_file(

    file: UploadFile = File(...),

    db: Session = Depends(get_db),

    current_user=Depends(require_role(GRADING_ROLES)),
):

    # -----------------------------------
    # Validate file extension
    # -----------------------------------
    file_extension = os.path.splitext(
        file.filename
    )[1].lower()

    # Invalid extension
    if file_extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(

            status_code=400,

            detail="Unsupported file type"
        )

    # -----------------------------------
    # Validate file size
    # -----------------------------------
    contents = file.file.read()

    # File too large
    if len(contents) > MAX_FILE_SIZE:

        raise HTTPException(

            status_code=400,

            detail="File too large"
        )

    # Reset file pointer
    file.file.seek(0)

    # -----------------------------------
    # Generate unique filename
    # -----------------------------------
    timestamp = datetime.utcnow().strftime(
        "%Y%m%d%H%M%S"
    )

    unique_filename = (
        f"{timestamp}_{file.filename}"
    )

    # -----------------------------------
    # File storage path
    # -----------------------------------
    file_location = (
        f"uploads/{unique_filename}"
    )

    # -----------------------------------
    # Save file to disk
    # -----------------------------------
    with open(file_location, "wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    # -----------------------------------
    # Public file URL
    # -----------------------------------
    file_url = (
        f"http://127.0.0.1:8000/uploads/{unique_filename}"
    )

    # -----------------------------------
    # Create DB object
    # -----------------------------------
    uploaded_file = UploadedFile(

        filename=unique_filename,

        file_url=file_url,

        owner_id=current_user["id"]
    )

    # -----------------------------------
    # Save to database
    # -----------------------------------
    db.add(uploaded_file)

    db.commit()

    db.refresh(uploaded_file)

    # -----------------------------------
    # Return response
    # -----------------------------------
    return uploaded_file


# -----------------------------------
# Get uploads belonging
# to authenticated user
# -----------------------------------
@router.get(
    "/uploads",
    response_model=list[UploadResponse]
)
def get_uploads(

    db: Session = Depends(get_db),

    current_user = Depends(get_current_user)
):

    # Fetch uploads for current user
    uploads = (

        db.query(UploadedFile)

        .filter(
            UploadedFile.owner_id
            == current_user["id"]
        )

        .all()
    )

    return uploads