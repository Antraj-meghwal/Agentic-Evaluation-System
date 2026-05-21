"""Celery tasks for batch processing."""

from core.logging import logger
from tasks.celery_app import celery_app


@celery_app.task(bind=True, max_retries=1)
def process_upload_batch_task(
    self,
    upload_id: int,
    file_path: str,
    rubric_path: str | None = None,
    rubric_json: dict | None = None,
    owner_email: str = "system",
):
    """Celery wrapper — delegates to shared runner (updates graded/failed)."""
    from services.job_runner import run_tribunal_and_update_status

    logger.info("Celery grading started for upload %s", upload_id)
    try:
        run_tribunal_and_update_status(
            upload_id,
            file_path,
            rubric_path=rubric_path,
            rubric_json=rubric_json,
            owner_email=owner_email,
        )
    except Exception as exc:
        logger.error("Celery task failed for upload %s: %s", upload_id, exc)
        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc, countdown=15) from exc
        raise
