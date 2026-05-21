"""Grading and multi-model pipeline API routes."""

import json
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from core.constants import GRADING_ROLES, REVIEW_ROLES
from db.session import SessionLocal
from dependencies import get_db, require_role
from models.grading_result import GradingResult
from models.question_crop import QuestionCrop
from models.upload_model import UploadedFile
from services.pipeline import run_extract_phase
from services.pipeline.schemas import GradingRubric
from core.config import settings
from services.job_runner import (
    celery_workers_available,
    get_celery_task_state,
    run_tribunal_and_update_status,
)
from services.tribunal_runner import resolve_rubric_path, run_tribunal_for_upload

router = APIRouter(tags=["grading"])


def _queue_tribunal_job(
    upload: UploadedFile,
    *,
    file_path: str,
    rubric_path: str | None,
    rubric_json: dict | None,
    owner_email: str,
    background_tasks: BackgroundTasks,
) -> dict:
    """Use Celery if a worker is running; otherwise run in-process (no stuck queue)."""
    owner = owner_email or "system"
    if celery_workers_available():
        from tasks.batch_tasks import process_upload_batch_task

        task = process_upload_batch_task.delay(
            upload_id=upload.id,
            file_path=file_path,
            rubric_path=rubric_path,
            rubric_json=rubric_json,
            owner_email=owner,
        )
        return {
            "status": "queued",
            "mode": "celery",
            "task_id": task.id,
            "upload_id": upload.id,
            "message": "Queued on Celery worker.",
        }

    background_tasks.add_task(
        run_tribunal_and_update_status,
        upload.id,
        file_path,
        rubric_path=rubric_path,
        rubric_json=rubric_json,
        owner_email=owner,
    )
    return {
        "status": "started",
        "mode": "background",
        "task_id": f"bg-{upload.id}",
        "upload_id": upload.id,
        "message": (
            "No Celery worker detected — running grading in the API process. "
            "Use “Run Tribunal (now)” for synchronous grading, or start ./scripts/run_celery.sh."
        ),
    }


def _upload_file_path(upload: UploadedFile) -> str:
    return str(Path(settings.UPLOAD_DIR) / upload.filename)


def _rubric_path_for_upload(upload: UploadedFile) -> str | None:
    return resolve_rubric_path(upload.rubric_path)


@router.post("/extract/{upload_id}")
def pipeline_extract(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(REVIEW_ROLES)),
):
    """Step 1 — EXTRACT: PDF → crops → OCR → context assembly."""
    upload = db.query(UploadedFile).filter(UploadedFile.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    try:
        result = run_extract_phase(
            upload_id=upload.id,
            file_path=_upload_file_path(upload),
            rubric_path=_rubric_path_for_upload(upload),
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    upload.status = "extracted"
    db.commit()
    return result.model_dump()


@router.post("/extract/{upload_id}/rubric")
async def pipeline_extract_with_rubric(
    upload_id: int,
    rubric: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(GRADING_ROLES)),
):
    """EXTRACT with instructor-provided rubric JSON."""
    upload = db.query(UploadedFile).filter(UploadedFile.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    try:
        rubric_data = json.loads(await rubric.read())
        GradingRubric.model_validate(rubric_data)
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid rubric JSON: {exc}") from exc

    result = run_extract_phase(
        upload_id=upload.id,
        file_path=_upload_file_path(upload),
        rubric_json=rubric_data,
    )
    upload.status = "extracted"
    db.commit()
    return result.model_dump()


@router.post("/run/{upload_id}")
def pipeline_run_tribunal(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(GRADING_ROLES)),
):
    """
    Full pipeline — EXTRACT + Tribunal (grader + critic) + DB persist + plagiarism scan.
    """
    upload = db.query(UploadedFile).filter(UploadedFile.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    try:
        result = run_tribunal_for_upload(
            upload_id=upload.id,
            file_path=_upload_file_path(upload),
            rubric_path=_rubric_path_for_upload(upload),
            owner_email=current_user.get("email") or str(current_user.get("id")),
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    upload.status = "graded"
    db.commit()
    return result


@router.post("/run/{upload_id}/rubric")
async def pipeline_run_with_rubric(
    upload_id: int,
    rubric: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(GRADING_ROLES)),
):
    """Full tribunal pipeline with custom rubric JSON."""
    upload = db.query(UploadedFile).filter(UploadedFile.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    try:
        rubric_data = json.loads(await rubric.read())
        GradingRubric.model_validate(rubric_data)
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid rubric JSON: {exc}") from exc

    try:
        result = run_tribunal_for_upload(
            upload_id=upload.id,
            file_path=_upload_file_path(upload),
            rubric_json=rubric_data,
            owner_email=current_user.get("email") or str(current_user.get("id")),
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    upload.status = "graded"
    db.commit()
    return result


@router.post("/run-async/{upload_id}")
def pipeline_run_async(
    upload_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(GRADING_ROLES)),
):
    """Run full pipeline in background (Celery if worker up, else in API process)."""
    upload = db.query(UploadedFile).filter(UploadedFile.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    upload.status = "processing"
    db.commit()

    return _queue_tribunal_job(
        upload,
        file_path=_upload_file_path(upload),
        rubric_path=_rubric_path_for_upload(upload),
        rubric_json=None,
        owner_email=current_user.get("email") or str(current_user.get("id")),
        background_tasks=background_tasks,
    )


@router.post("/run-async/{upload_id}/rubric")
async def pipeline_run_async_with_rubric(
    upload_id: int,
    background_tasks: BackgroundTasks,
    rubric: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(GRADING_ROLES)),
):
    """Background pipeline with custom rubric JSON."""
    upload = db.query(UploadedFile).filter(UploadedFile.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    try:
        rubric_data = json.loads(await rubric.read())
        GradingRubric.model_validate(rubric_data)
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid rubric JSON: {exc}") from exc

    upload.status = "processing"
    db.commit()

    return _queue_tribunal_job(
        upload,
        file_path=_upload_file_path(upload),
        rubric_path=None,
        rubric_json=rubric_data,
        owner_email=current_user.get("email") or str(current_user.get("id")),
        background_tasks=background_tasks,
    )


@router.get("/task/{task_id}")
def get_task_status(
    task_id: str,
    _user=Depends(require_role(REVIEW_ROLES)),
):
    """Poll Celery task state (PENDING = no worker picked up the job)."""
    if task_id.startswith("bg-"):
        return {
            "task_id": task_id,
            "state": "STARTED",
            "ready": False,
            "mode": "background",
            "message": "Running inside API process; refresh upload status.",
        }
    return get_celery_task_state(task_id)


@router.post("/reset-status/{upload_id}")
def reset_processing_status(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(GRADING_ROLES)),
):
    """Unstick uploads left in processing (e.g. Celery never ran)."""
    upload = db.query(UploadedFile).filter(UploadedFile.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    if upload.status not in ("processing", "failed"):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot reset status '{upload.status}'",
        )
    upload.status = "uploaded"
    db.commit()
    return {"upload_id": upload_id, "status": upload.status}


@router.get("/results/{upload_id}")
def get_grading_results(
    upload_id: int,
    _user=Depends(require_role(REVIEW_ROLES)),
):
    """List tribunal grading results for an upload."""
    db = SessionLocal()
    try:
        rows = db.query(GradingResult).all()
        items = []
        for gr in rows:
            meta = gr.coordinator_output or {}
            if int(meta.get("upload_id") or -1) != upload_id:
                continue
            crop = (
                db.query(QuestionCrop)
                .filter(QuestionCrop.id == gr.question_crop_id)
                .first()
            )
            image_path = crop.crop_image_path if crop else None
            image_url = None
            if image_path:
                image_url = f"/{image_path.lstrip('/')}"
            items.append(
                {
                    "grading_result_id": str(gr.id),
                    "question_id": crop.question_id if crop else None,
                    "score": gr.final_score,
                    "max_score": gr.max_score,
                    "confidence": gr.confidence_score,
                    "feedback": gr.final_feedback,
                    "requires_human_review": gr.requires_human_review,
                    "resolution_status": gr.resolution_status.value,
                    "criteria_breakdown": (gr.grader_output or {}).get(
                        "criteria_breakdown", []
                    ),
                    "crop_image_url": image_url,
                    "escalation_reasons": meta.get("escalation_reasons", []),
                    "plagiarism_flags": meta.get("plagiarism_flags", []),
                }
            )
        return {"upload_id": upload_id, "results": items}
    finally:
        db.close()
