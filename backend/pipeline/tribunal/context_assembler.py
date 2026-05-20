from models.question_crop import QuestionCrop
from models.submission import Submission
from schemas.rubric_schema import (
    QuestionSchema,
    RubricSchema
)

from pipeline.tribunal.rag_store import (
    RAGVectorStore
)


def build_grading_context(
    crop: QuestionCrop,
    submission: Submission,
    rubric: RubricSchema
):
    """
    Build canonical grading context
    for tribunal agents.
    """

    matched_question = None

    for question in rubric.questions:

        if question.q_id == crop.question_id:
            matched_question = question
            break

    if matched_question is None:
        raise ValueError(
            f"No rubric question found for "
            f"{crop.question_id}"
        )

    rag_store = RAGVectorStore()

    similar_answers = (
        rag_store.retrieve_similar_answers(
        question_id=crop.question_id,
        query_text=crop.ocr_text or ""
        )
    )

    context = {
        "student_id": submission.student_id,

        "question_id": crop.question_id,

        "rubric": matched_question.model_dump(),

        "ocr_text": crop.ocr_text,

        "crop_image_path": crop.crop_image_path,

        "content_type": (
            matched_question.content_type.value
        ),

        "bypass_ocr": (
            matched_question.bypass_ocr
        ),

        "similar_answers": similar_answers
    }

    return context