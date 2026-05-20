"""Grading and multi-model pipeline API routes."""

import json
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from dependencies import get_db, require_role
from models.upload_model import UploadedFile
from services.pipeline import run_extract_phase
from services.pipeline.schemas import GradingRubric
from services.vision.vision_router import prepare_document_for_grading
from services.vision_grading_service import grade_answer_sheet

router = APIRouter(tags=["grading"])

DEFAULT_RUBRIC = Path(__file__).resolve().parents[2] / "examples" / "sample_rubric.json"


@router.post("/extract/{upload_id}")
def pipeline_extract(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["instructor", "ta"])),
):
    """
    Step 1 — EXTRACT phase only.
    PDF → page crops → HF OCR → context assembler.
    """
    upload = db.query(UploadedFile).filter(UploadedFile.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")

    file_path = upload.file_url.replace("http://127.0.0.1:8000/", "").lstrip("/")
    rubric_path = str(DEFAULT_RUBRIC) if DEFAULT_RUBRIC.exists() else None

    try:
        result = run_extract_phase(
            upload_id=upload.id,
            file_path=file_path,
            rubric_path=rubric_path,
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
    current_user=Depends(require_role(["instructor"])),
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

    file_path = upload.file_url.replace("http://127.0.0.1:8000/", "").lstrip("/")
    result = run_extract_phase(
        upload_id=upload.id,
        file_path=file_path,
        rubric_json=rubric_data,
    )
    upload.status = "extracted"
    db.commit()
    return result.model_dump()


@router.post("/grade/{upload_id}")
def grade_uploaded_answer(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["instructor"])),
):
    """Legacy single-model grade (Qwen-VL). Tribunal uses /pipeline/run in Step 2."""
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
        "note": "Use POST /grading/extract/{id} for full pipeline; Tribunal in Step 2.",
    }
