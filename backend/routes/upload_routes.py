"""Upload endpoints — single file, bulk PDFs, optional rubric JSON."""

import json
import os
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from core.constants import ALLOWED_EXTENSIONS, GRADING_ROLES, REVIEW_ROLES
from dependencies import get_current_user, get_db, require_role
from models.upload_model import UploadedFile
from schemas.upload_schema import BulkUploadResponse, UploadResponse
from services.pipeline.schemas import GradingRubric
from services.storage_service import MAX_UPLOAD_BYTES, get_storage, unique_key

router = APIRouter()


def _validate_extension(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    return ext


def _read_bounded(upload: UploadFile) -> bytes:
    data = upload.file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large (max {MAX_UPLOAD_BYTES // (1024 * 1024)} MB)",
        )
    upload.file.seek(0)
    return data


def _save_rubric(rubric: UploadFile) -> str:
    data = _read_bounded(rubric)
    try:
        rubric_data = json.loads(data)
        GradingRubric.model_validate(rubric_data)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail="Invalid rubric JSON") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid rubric schema: {exc}") from exc

    storage = get_storage()
    key = unique_key(rubric.filename or "rubric.json", prefix="rubrics")
    storage.save_bytes(key, data, content_type="application/json")
    return key


def _persist_upload(
    db: Session,
    *,
    filename: str,
    file_url: str,
    owner_id: int,
    rubric_path: str | None = None,
) -> UploadedFile:
    row = UploadedFile(
        filename=filename,
        file_url=file_url,
        owner_id=owner_id,
        rubric_path=rubric_path,
        status="uploaded",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.post("/upload", response_model=UploadResponse)
def upload_file(
    file: UploadFile = File(...),
    rubric: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(GRADING_ROLES)),
):
    _validate_extension(file.filename or "")
    data = _read_bounded(file)
    storage = get_storage()
    key = unique_key(file.filename or "exam.pdf")
    file_url = storage.save_bytes(key, data, content_type=file.content_type)

    rubric_path = _save_rubric(rubric) if rubric else None
    return _persist_upload(
        db,
        filename=key,
        file_url=file_url,
        owner_id=current_user["id"],
        rubric_path=rubric_path,
    )


@router.post("/upload/bulk", response_model=BulkUploadResponse)
async def upload_bulk(
    files: Annotated[list[UploadFile], File(...)],
    rubric: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(require_role(GRADING_ROLES)),
):
    if not files:
        raise HTTPException(status_code=400, detail="At least one file is required")
    if len(files) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 files per bulk upload")

    rubric_path = _save_rubric(rubric) if rubric else None
    storage = get_storage()
    created: list[UploadResponse] = []

    for upload in files:
        _validate_extension(upload.filename or "")
        data = _read_bounded(upload)
        key = unique_key(upload.filename or "exam.pdf")
        file_url = storage.save_bytes(key, data, content_type=upload.content_type)
        row = _persist_upload(
            db,
            filename=key,
            file_url=file_url,
            owner_id=current_user["id"],
            rubric_path=rubric_path,
        )
        created.append(UploadResponse.model_validate(row))

    return BulkUploadResponse(uploaded=len(created), items=created)


@router.get("/api/uploads/{upload_id}", response_model=UploadResponse)
def get_upload(
    upload_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    upload = db.query(UploadedFile).filter(UploadedFile.id == upload_id).first()
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    role = (current_user.get("role") or "").lower()
    if role not in {r.lower() for r in REVIEW_ROLES}:
        if upload.owner_id != current_user["id"]:
            raise HTTPException(status_code=403, detail="Not allowed")
    return upload


@router.get("/api/uploads", response_model=list[UploadResponse])
def get_uploads(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    role = (current_user.get("role") or "").lower()
    q = db.query(UploadedFile)
    if role not in {r.lower() for r in REVIEW_ROLES}:
        q = q.filter(UploadedFile.owner_id == current_user["id"])
    return q.order_by(UploadedFile.created_at.desc()).all()
