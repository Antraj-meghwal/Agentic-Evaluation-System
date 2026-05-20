from pydantic import BaseModel


class ReviewDecisionSchema(
    BaseModel
):

    reviewer_id: str | None = None

    updated_score: int

    review_notes: str = ""