from fastapi import APIRouter

from db.session import SessionLocal

from models.question_crop import (
    QuestionCrop
)

from models.grading_result import (
    GradingResult
)


router = APIRouter()


@router.get(
    "/crop-status/{crop_id}"
)
def get_crop_status(
    crop_id: str
):

    db = SessionLocal()

    try:

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

        grading_result = (
            db.query(GradingResult)
            .filter(
                GradingResult.question_crop_id
                == crop.id
            )
            .first()
        )

        response = {

            "crop_id":
            str(crop.id),

            "status":
            crop.status.value,

            "ocr_text":
            crop.ocr_text,

            "grading_complete":
            grading_result is not None
        }

        if grading_result:

            response["grading_result"] = {

                "score":
                grading_result.final_score,

                "max_score":
                grading_result.max_score,

                "confidence":
                grading_result.confidence_score,

                "requires_human_review":
                (
                    grading_result
                    .requires_human_review
                ),

                "resolution_status":
                (
                    grading_result
                    .resolution_status.value
                )
            }

        return response

    finally:

        db.close()