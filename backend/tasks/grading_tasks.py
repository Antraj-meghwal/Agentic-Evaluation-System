from db.session import SessionLocal

from models.question_crop import (
    CropStatus,
    QuestionCrop
)

from pipeline.extraction.ocr_pipeline import (
    run_ocr_pipeline
)

from pipeline.tribunal.context_assembler import (
    build_grading_context
)

from pipeline.tribunal.grading_pipeline import (
    run_grading_pipeline
)

from services.rubric_service import (
    load_rubric
)

from tasks.celery_app import (
    celery_app
)
from core.logging import logger

@celery_app.task(
    bind=True,

    autoretry_for=(Exception,),

    retry_backoff=True,

    retry_backoff_max=600,

    retry_jitter=True,

    max_retries=3
)
def process_crop_task(
    self,
    crop_id: str,
    rubric_path: str
):
    """
    Full async crop processing task.
    """

    db = SessionLocal()

    crop = None

    try:

        crop = (
            db.query(QuestionCrop)
            .filter(
                QuestionCrop.id == crop_id
            )
            .first()
        )

        if not crop:

            print(
                f"Crop not found: {crop_id}"
            )

            return

        submission = crop.submission

        # --------------------------------
        # OCR Stage
        # --------------------------------

        crop = run_ocr_pipeline(
            db=db,
            crop=crop
        )

        # --------------------------------
        # Rubric Loading
        # --------------------------------

        rubric = load_rubric(
            rubric_path
        )

        # --------------------------------
        # Context Assembly
        # --------------------------------

        grading_context = (
            build_grading_context(
                crop=crop,
                submission=submission,
                rubric=rubric
            )
        )

        # --------------------------------
        # Tribunal Grading
        # --------------------------------

        run_grading_pipeline(
            db=db,
            crop=crop,
            grading_context=grading_context
        )

        logger.info(
            f"Completed processing "
            f"for crop {crop_id}"
        )
    except Exception as e:

        print(
            f"Task failed for crop "
            f"{crop_id}: {str(e)}"
        )

        if crop:

            if self.request.retries >= 2:

                crop.status = (
                    CropStatus.FAILED
                )

            else:

                crop.status = (
                    CropStatus.RETRYING
                )

            db.commit()

        raise e

    finally:

        db.close()