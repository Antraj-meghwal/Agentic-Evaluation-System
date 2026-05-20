from fastapi import APIRouter, Depends

from db.session import SessionLocal

from models.grading_result import (
    GradingResult
)
from schemas.review_schema import (
    ReviewDecisionSchema
)

from models.review_action import (
    ReviewAction,
    ReviewActionType
)
from dependencies import get_current_user

router = APIRouter()

@router.post(
    "/override/{grading_result_id}"
)
def override_grade(
    grading_result_id: str,
    review_data: ReviewDecisionSchema,
    _user=Depends(get_current_user),
):

    db = SessionLocal()

    try:

        grading_result = (
            db.query(GradingResult)
            .filter(
                GradingResult.id
                == grading_result_id
            )
            .first()
        )

        if not grading_result:

            return {
                "error":
                "Result not found"
            }

        original_score = (
            grading_result.final_score
        )

        grading_result.final_score = (
            review_data.updated_score
        )

        grading_result.requires_human_review = (
            False
        )

        review_action = ReviewAction(

            grading_result_id=
            grading_result.id,

            reviewer_id=
            review_data.reviewer_id,

            action_type=
            ReviewActionType.OVERRIDDEN,

            original_score=
            original_score,

            updated_score=
            review_data.updated_score,

            review_notes=
            review_data.review_notes
        )

        db.add(review_action)

        db.commit()

        return {
            "message":
            "Override successful"
        }

    finally:

        db.close()
@router.get(
    "/review-queue"
)
def get_review_queue(_user=Depends(get_current_user)):

    db = SessionLocal()

    try:

        review_items = (
            db.query(GradingResult)
            .filter(
                GradingResult
                .requires_human_review
                == True
            )
            .all()
        )

        response = []

        for item in review_items:

            response.append(
                {

                    "grading_result_id":
                    str(item.id),

                    "score":
                    item.final_score,

                    "max_score":
                    item.max_score,

                    "confidence":
                    item.confidence_score,

                    "feedback":
                    item.final_feedback,

                    "resolution_status":
                    item
                    .resolution_status
                    .value,

                    "escalation_reasons":
                    (
                        item
                        .coordinator_output
                        .get(
                            "escalation_reasons",
                            []
                        )
                    )
                }
            )

        return response

    finally:

        db.close()