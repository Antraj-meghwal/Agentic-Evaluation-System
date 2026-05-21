"""Celery tasks for batch processing."""

from core.logging import logger
from db.session import SessionLocal
from models.upload_model import UploadedFile
from services.tribunal_runner import run_tribunal_for_upload
from tasks.celery_app import celery_app


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
    max_retries=3
)
def process_upload_batch_task(
    self,
    upload_id: int,
    file_path: str,
    rubric_path: str | None = None,
    rubric_json: dict | None = None,
    owner_email: str = "system",
):
    """
    Async wrapper for the full Tribunal grading pipeline.
    """
    logger.info(f"Starting async batch grading for upload {upload_id}")
    db = SessionLocal()
    upload = None
    try:
        upload = db.query(UploadedFile).filter(UploadedFile.id == upload_id).first()
        if not upload:
            logger.error(f"Upload {upload_id} not found for batch processing.")
            return
        
        # Run the full pipeline
        run_tribunal_for_upload(
            upload_id=upload_id,
            file_path=file_path,
            rubric_path=rubric_path,
            rubric_json=rubric_json,
            owner_email=owner_email,
        )
        
        # Update status
        upload.status = "graded"
        db.commit()
        logger.info(f"Successfully completed async batch grading for upload {upload_id}")
        
    except Exception as e:
        logger.error(f"Task failed for upload {upload_id}: {str(e)}")
        if upload:
            # If we're out of retries, mark as failed permanently
            if self.request.retries >= self.max_retries:
                upload.status = "failed"
            db.commit()
        raise e
    finally:
        db.close()
