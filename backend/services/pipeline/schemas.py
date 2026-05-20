"""Structured types for the multi-model grading pipeline."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class QuestionType(str, Enum):
    TEXT = "text"
    DIAGRAM = "diagram"
    MIXED = "mixed"


class RubricCriterion(BaseModel):
    id: str
    description: str
    max_points: float
    required_keywords: list[str] = Field(default_factory=list)


class RubricQuestion(BaseModel):
    id: str
    title: str
    max_points: float
    question_type: QuestionType = QuestionType.TEXT
    criteria: list[RubricCriterion] = Field(default_factory=list)


class GradingRubric(BaseModel):
    """Instructor-uploaded rubric JSON (per PDF guide)."""

    exam_id: str
    course: str = ""
    questions: list[RubricQuestion]


class PageCrop(BaseModel):
    page_index: int
    image_path: str
    width: int | None = None
    height: int | None = None


class QuestionCrop(BaseModel):
    question_id: str
    page_index: int
    image_path: str
    bypass_ocr: bool = False


class OcrResult(BaseModel):
    question_id: str
    transcript: str
    model_id: str
    confidence: float = 0.0
    raw_response: dict[str, Any] | None = None


class GradingContext(BaseModel):
    """Merged context fed into the Tribunal (Step 2)."""

    upload_id: int
    question: RubricQuestion
    crop: QuestionCrop
    ocr: OcrResult | None = None
    rubric_json: dict[str, Any] = Field(default_factory=dict)


class ExtractPhaseResult(BaseModel):
    upload_id: int
    pages: list[PageCrop]
    questions: list[QuestionCrop]
    contexts: list[GradingContext]
    status: str = "extracted"
