"""Gradebook export API routes — CSV, Canvas CSV, and JSON downloads."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse

from core.constants import REVIEW_ROLES
from db.session import SessionLocal
from dependencies import require_role
from services.export_service import (
    export_canvas_csv,
    export_gradebook_csv,
    export_gradebook_json,
)

router = APIRouter()


@router.get("/csv/{upload_id}")
def download_gradebook_csv(
    upload_id: int,
    _user=Depends(require_role(REVIEW_ROLES)),
):
    """Download a standard gradebook CSV for a specific upload."""
    db = SessionLocal()
    try:
        csv_content = export_gradebook_csv(db, upload_id=upload_id)
        if not csv_content.strip():
            raise HTTPException(status_code=404, detail="No grading results found for this upload.")

        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="gradebook_upload_{upload_id}.csv"'
            },
        )
    finally:
        db.close()


@router.get("/canvas-csv/{upload_id}")
def download_canvas_csv(
    upload_id: int,
    _user=Depends(require_role(REVIEW_ROLES)),
):
    """Download a Canvas LMS-compatible CSV for a specific upload."""
    db = SessionLocal()
    try:
        csv_content = export_canvas_csv(db, upload_id=upload_id)
        if not csv_content.strip():
            raise HTTPException(status_code=404, detail="No grading results found for this upload.")

        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="canvas_grades_upload_{upload_id}.csv"'
            },
        )
    finally:
        db.close()


@router.get("/json/{upload_id}")
def download_gradebook_json(
    upload_id: int,
    _user=Depends(require_role(REVIEW_ROLES)),
):
    """Download a full JSON gradebook for a specific upload."""
    db = SessionLocal()
    try:
        data = export_gradebook_json(db, upload_id=upload_id)
        if not data.get("results"):
            raise HTTPException(status_code=404, detail="No grading results found for this upload.")

        return JSONResponse(
            content=data,
            headers={
                "Content-Disposition": f'attachment; filename="gradebook_upload_{upload_id}.json"'
            },
        )
    finally:
        db.close()


@router.get("/batch/csv/{batch_id}")
def download_batch_csv(
    batch_id: str,
    _user=Depends(require_role(REVIEW_ROLES)),
):
    """Download a standard gradebook CSV for an entire batch."""
    db = SessionLocal()
    try:
        csv_content = export_gradebook_csv(db, batch_id=batch_id)
        if not csv_content.strip():
            raise HTTPException(status_code=404, detail="No grading results found for this batch.")

        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="gradebook_batch_{batch_id}.csv"'
            },
        )
    finally:
        db.close()


@router.get("/batch/canvas-csv/{batch_id}")
def download_batch_canvas_csv(
    batch_id: str,
    _user=Depends(require_role(REVIEW_ROLES)),
):
    """Download a Canvas LMS-compatible CSV for an entire batch."""
    db = SessionLocal()
    try:
        csv_content = export_canvas_csv(db, batch_id=batch_id)
        if not csv_content.strip():
            raise HTTPException(status_code=404, detail="No grading results found for this batch.")

        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="canvas_grades_batch_{batch_id}.csv"'
            },
        )
    finally:
        db.close()


@router.get("/batch/json/{batch_id}")
def download_batch_json(
    batch_id: str,
    _user=Depends(require_role(REVIEW_ROLES)),
):
    """Download a full JSON gradebook for an entire batch."""
    db = SessionLocal()
    try:
        data = export_gradebook_json(db, batch_id=batch_id)
        if not data.get("results"):
            raise HTTPException(status_code=404, detail="No grading results found for this batch.")

        return JSONResponse(
            content=data,
            headers={
                "Content-Disposition": f'attachment; filename="gradebook_batch_{batch_id}.json"'
            },
        )
    finally:
        db.close()


@router.get("/summary/{upload_id}")
def get_gradebook_summary(
    upload_id: int,
    _user=Depends(require_role(REVIEW_ROLES)),
):
    """Get a summary of grading results for an upload (no download, just JSON)."""
    db = SessionLocal()
    try:
        data = export_gradebook_json(db, upload_id=upload_id)
        return {
            "upload_id": upload_id,
            "summary": data["summary"],
            "result_count": len(data["results"]),
        }
    finally:
        db.close()
