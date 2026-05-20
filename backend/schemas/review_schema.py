from pydantic import BaseModel


class ReviewDecisionSchema(
    BaseModel
):

    reviewer_id: str

    updated_score: int

    review_notes: str