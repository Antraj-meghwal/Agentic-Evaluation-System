from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class ContentType(str, Enum):
    TEXT = "TEXT"
    DIAGRAM = "DIAGRAM"
    MIXED = "MIXED"


class CriterionSchema(BaseModel):
    id: str
    description: str
    points: int


class AnswerRegionSchema(BaseModel):
    page: int

    bbox: List[float] = Field(
        ...,
        min_length=4,
        max_length=4
    )


class QuestionSchema(BaseModel):
    q_id: str

    max_points: int

    content_type: ContentType = ContentType.TEXT

    bypass_ocr: bool = False

    criteria: List[CriterionSchema]

    answer_region: AnswerRegionSchema


class RubricSchema(BaseModel):
    exam_id: str

    questions: List[QuestionSchema]