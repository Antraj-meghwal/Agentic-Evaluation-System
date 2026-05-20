from fastapi import APIRouter

from db.session import SessionLocal

from models.grading_result import (
    GradingResult
)


router = APIRouter()


@router.get(
    "/results"
)
def get_results():

    db = SessionLocal()

    try:

        results = (
            db.query(GradingResult)
            .all()
        )

        response = []

        for result in results:

            response.append({

                "grading_result_id":
                str(result.id),

                "score":
                result.final_score,

                "max_score":
                result.max_score,

                "confidence":
                result.confidence_score,

                "resolution_status":
                result
                .resolution_status
                .value,

                "requires_human_review":
                result
                .requires_human_review,

                "feedback":
                result.final_feedback
            })

        return response

    finally:

        db.close()