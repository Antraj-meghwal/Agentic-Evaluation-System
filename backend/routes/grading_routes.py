# FastAPI tools
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

# Database session
from sqlalchemy.orm import Session

# Dependencies
from dependencies import (
    get_db,
    require_role
)

# Upload model
from models.upload_model import UploadedFile

# Vision preprocessing
from services.vision.vision_router import (
    prepare_document_for_grading
)

# Vision grading
from services.vision_grading_service import (
    grade_answer_sheet
)


# Create router
router = APIRouter()


# -----------------------------------
# Grade uploaded answer sheet
# -----------------------------------
@router.post("/grade/{upload_id}")
def grade_uploaded_answer(

    upload_id: int,

    db: Session = Depends(get_db),

    current_user = Depends(
        require_role(["instructor"])
    )
):

    # Fetch upload
    upload = (

        db.query(UploadedFile)

        .filter(
            UploadedFile.id == upload_id
        )

        .first()
    )

    # Upload not found
    if not upload:

        raise HTTPException(

            status_code=404,

            detail="Upload not found"
        )

    # Prepare images
    processed_images = (
        prepare_document_for_grading(
            upload.file_url.replace(
                "http://127.0.0.1:8000/",
                ""
            )
        )
    )

    # Example rubric
    rubric = """

    Award marks for:
    - correctness
    - explanation
    - examples
    - clarity
    """

    # Grade first page
    grading_result = grade_answer_sheet(

        processed_images[0],

        rubric
    )

    return {

        "upload_id": upload.id,

        "grading_result": grading_result
    }