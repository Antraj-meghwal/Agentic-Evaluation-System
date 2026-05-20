from fastapi import APIRouter

from db.session import SessionLocal

from models.batch import Batch
from models.question_crop import QuestionCrop
from models.submission import Submission


router = APIRouter()


@router.get(
    "/batch-status/{batch_id}"
)
def get_batch_status(
    batch_id: str
):

    db = SessionLocal()

    try:

        batch = (
            db.query(Batch)
            .filter(
                Batch.id == batch_id
            )
            .first()
        )

        if not batch:

            return {
                "error":
                "Batch not found"
            }

        submissions = (
            db.query(Submission)
            .filter(
                Submission.batch_id
                == batch.id
            )
            .all()
        )

        submission_ids = [
            s.id for s in submissions
        ]

        crops = (
            db.query(QuestionCrop)
            .filter(
                QuestionCrop.submission_id
                .in_(submission_ids)
            )
            .all()
        )

        total_crops = len(crops)

        graded_crops = len([
            c for c in crops
            if c.status.value == "GRADED"
        ])

        failed_crops = len([
            c for c in crops
            if c.status.value == "FAILED"
        ])

        retrying_crops = len([
            c for c in crops
            if c.status.value == "RETRYING"
        ])

        progress = 0

        if total_crops > 0:

            progress = round(
                (
                    graded_crops
                    / total_crops
                ) * 100,
                2
            )

        return {

            "batch_id":
            str(batch.id),

            "exam_name":
            batch.exam_name,

            "status":
            batch.status.value,

            "total_submissions":
            len(submissions),

            "total_crops":
            total_crops,

            "graded_crops":
            graded_crops,

            "failed_crops":
            failed_crops,

            "retrying_crops":
            retrying_crops,

            "progress_percentage":
            progress
        }

    finally:

        db.close()