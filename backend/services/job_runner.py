"""Background grading: Celery when available, else FastAPI BackgroundTasks."""

from __future__ import annotations

import logging
from typing import Any

from core.config import settings
from db.session import SessionLocal
from models.upload_model import UploadedFile
from services.tribunal_runner import run_tribunal_for_upload

logger = logging.getLogger(__name__)


def redis_available() -> bool:
    try:
        import redis

        client = redis.from_url(settings.REDIS_URL, socket_connect_timeout=1)
        client.ping()
        return True
    except Exception:
        return False


def celery_workers_available() -> bool:
    """True only if Redis is up and at least one Celery worker responds."""
    if not redis_available():
        return False
    try:
        from tasks.celery_app import celery_app

        inspect = celery_app.control.inspect(timeout=1.0)
        ping = inspect.ping()
        return bool(ping)
    except Exception as exc:
        logger.debug("Celery inspect failed: %s", exc)
        return False


def run_tribunal_and_update_status(
    upload_id: int,
    file_path: str,
    *,
    rubric_path: str | None = None,
    rubric_json: dict | None = None,
    owner_email: str = "system",
) -> None:
    """Run full pipeline and set upload status to graded or failed."""
    db = SessionLocal()
    try:
        upload = db.query(UploadedFile).filter(UploadedFile.id == upload_id).first()
        if not upload:
            logger.error("Upload %s not found for background grading", upload_id)
            return

        run_tribunal_for_upload(
            upload_id=upload_id,
            file_path=file_path,
            rubric_path=rubric_path,
            rubric_json=rubric_json,
            owner_email=owner_email,
        )
        upload = db.query(UploadedFile).filter(UploadedFile.id == upload_id).first()
        if upload:
            upload.status = "graded"
            db.commit()
        logger.info("Background grading completed for upload %s", upload_id)
    except Exception as exc:
        logger.exception("Background grading failed for upload %s: %s", upload_id, exc)
        upload = db.query(UploadedFile).filter(UploadedFile.id == upload_id).first()
        if upload:
            upload.status = "failed"
            db.commit()
    finally:
        db.close()


def get_celery_task_state(task_id: str) -> dict[str, Any]:
    from tasks.celery_app import celery_app

    result = celery_app.AsyncResult(task_id)
    state = result.state or "PENDING"
    payload: dict[str, Any] = {
        "task_id": task_id,
        "state": state,
        "ready": result.ready(),
        "successful": result.successful() if result.ready() else None,
    }
    if result.failed():
        payload["error"] = str(result.result) if result.result else "Task failed"
    return payload
