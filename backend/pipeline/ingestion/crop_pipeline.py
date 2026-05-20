from pathlib import Path
from models.submission import SubmissionStatus
from sqlalchemy.orm import Session

from models.question_crop import (
    CropStatus,
    QuestionCrop
)
from models.submission import Submission
from schemas.rubric_schema import RubricSchema
from services.pdf_service import crop_answer_region


def process_submission_crops(
    db: Session,
    submission: Submission,
    rubric: RubricSchema
):
    """
    Generate question crops for a submission
    based on rubric instructions.
    """

    generated_crops = []

    for question in rubric.questions:

        output_path = (
            f"uploads/processed/"
            f"{submission.student_id}_"
            f"{question.q_id}.png"
        )

        crop_answer_region(
            pdf_path=submission.original_pdf_path,
            page_number=question.answer_region.page - 1,
            bbox_norm=question.answer_region.bbox,
            output_path=output_path
        )

        crop = QuestionCrop(
            submission_id=submission.id,
            question_id=question.q_id,
            page_number=question.answer_region.page,
            crop_image_path=output_path,
            status=CropStatus.PENDING
        )

        db.add(crop)

        generated_crops.append(crop)

    submission.status = SubmissionStatus.CROPPED

    db.commit()

    for crop in generated_crops:
        db.refresh(crop)

    return generated_crops