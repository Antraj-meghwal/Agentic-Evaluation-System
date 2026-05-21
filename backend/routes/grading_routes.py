"""Grading and multi-model pipeline API routes."""

import json
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from core.constants import GRADING_ROLES, REVIEW_ROLES
from db.session import SessionLocal
from dependencies import get_db, require_role
from models.grading_result import GradingResult
from models.question_crop import QuestionCrop
from models.upload_model import UploadedFile
from services.pipeline import run_extract_phase
from services.pipeline.schemas import GradingRubric
from services.tribunal_runner import resolve_rubric_path, run_tribunal_for_upload
from services.vision.vision_router import prepare_document_for_grading
from services.vision_grading_service import grade_answer_sheet

router = APIRouter(tags=["grading"])

_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUBRIC = _ROOT / "examples" / "sample_rubric.json"
_FALLBACK_RUBRIC = Path(__file__).resolve().parents[1] / "data" / "rubrics" / "sample_rubric.json"


def _upload_file_path(upload: UploadedFile) -> str:
    return upload.file_url.replace("http://127.0.0.1:8000/", "").lstrip("/")


def _default_rubric_path() -> str | None:
    rubric_file = DEFAULT_RUBRIC if DEFAULT_RUBRIC.exists() else _FALLBACK_RUBRIC
    return str(rubric_file) if rubric_file.exists() else None


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
            rubric_path=_default_rubric_path(),
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
            rubric_path=resolve_rubric_path(),
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
    db: Session = Depends(get_db),
    current_user=Depends(require_role(GRADING_ROLES)),
):
    """
    Queue full pipeline asynchronously via Celery.
    """
    upload = db.query(UploadedFile).filter(UploadedFile.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    upload.status = "processing"
    db.commit()

    from tasks.batch_tasks import process_upload_batch_task
    task = process_upload_batch_task.delay(
        upload_id=upload.id,
        file_path=_upload_file_path(upload),
        rubric_path=resolve_rubric_path(),
        owner_email=current_user.get("email") or str(current_user.get("id")),
    )
    
    return {"status": "queued", "task_id": task.id, "upload_id": upload_id}


@router.post("/run-async/{upload_id}/rubric")
async def pipeline_run_async_with_rubric(
    upload_id: int,
    rubric: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(GRADING_ROLES)),
):
    """
    Queue full pipeline asynchronously with custom rubric JSON.
    """
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

    from tasks.batch_tasks import process_upload_batch_task
    task = process_upload_batch_task.delay(
        upload_id=upload.id,
        file_path=_upload_file_path(upload),
        rubric_json=rubric_data,
        owner_email=current_user.get("email") or str(current_user.get("id")),
    )

    return {"status": "queued", "task_id": task.id, "upload_id": upload_id}


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


@router.post("/grade/{upload_id}")
def grade_uploaded_answer(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(GRADING_ROLES)),
):
    """Legacy single-model grade (Qwen-VL). Prefer POST /grading/run/{id}."""
    upload = db.query(UploadedFile).filter(UploadedFile.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    processed_images = prepare_document_for_grading(
        upload.file_url.replace("http://127.0.0.1:8000/", ""),
        upload_id=upload.id,
    )

    rubric = """
    Award marks for:
    - correctness
    - explanation
    - examples
    - clarity
    """

    grading_result = grade_answer_sheet(processed_images[0], rubric)

    return {
        "upload_id": upload.id,
        "grading_result": grading_result,
        "note": "Use POST /grading/run/{id} for full Tribunal pipeline.",
    }
