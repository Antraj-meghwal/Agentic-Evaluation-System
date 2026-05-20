"""Merge OCR transcript, raw image path, and rubric into Tribunal input."""

from __future__ import annotations

from services.pipeline.schemas import (
    GradingContext,
    GradingRubric,
    OcrResult,
    QuestionCrop,
    RubricQuestion,
)


def match_question(
    crop: QuestionCrop,
    rubric: GradingRubric,
) -> RubricQuestion:
    for q in rubric.questions:
        if q.id == crop.question_id:
            return q
    # Fallback: map by page order
    idx = crop.page_index
    if idx < len(rubric.questions):
        return rubric.questions[idx]
    return RubricQuestion(
        id=crop.question_id,
        title=f"Question {crop.question_id}",
        max_points=10.0,
    )


def assemble_context(
    upload_id: int,
    crop: QuestionCrop,
    ocr: OcrResult | None,
    rubric: GradingRubric,
) -> GradingContext:
    question = match_question(crop, rubric)
    return GradingContext(
        upload_id=upload_id,
        question=question,
        crop=crop,
        ocr=ocr,
        rubric_json=rubric.model_dump(),
    )


def assemble_all(
    upload_id: int,
    crops: list[QuestionCrop],
    ocrs: dict[str, OcrResult],
    rubric: GradingRubric,
) -> list[GradingContext]:
    contexts: list[GradingContext] = []
    for crop in crops:
        ocr = ocrs.get(crop.question_id)
        contexts.append(assemble_context(upload_id, crop, ocr, rubric))
    return contexts
