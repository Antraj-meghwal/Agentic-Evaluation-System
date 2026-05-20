from fastapi import APIRouter

from db.session import SessionLocal

from models.question_crop import (
    QuestionCrop
)

from tasks.grading_tasks import (
    process_crop_task
)


router = APIRouter()


@router.post(
    "/process-crop/{crop_id}"
)
def process_crop(
    crop_id: str
):

    db = SessionLocal()

    crop = (
        db.query(QuestionCrop)
        .filter(
            QuestionCrop.id == crop_id
        )
        .first()
    )

    if not crop:

        return {
            "error":
            "Crop not found"
        }

    process_crop_task.delay(
        crop_id,
        "data/rubrics/sample_rubric.json"
    )

    return {
        "message":
        "Task submitted",

        "crop_id":
        crop_id
    }