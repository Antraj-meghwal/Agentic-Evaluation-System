"""Dashboard API for role-specific home screens."""

from fastapi import APIRouter, Depends

from core.constants import REVIEW_ROLES, ROLE_STUDENT
from db.session import SessionLocal
from dependencies import get_current_user, require_role
from services.dashboard_service import (
    get_professor_dashboard,
    get_review_stats,
    get_student_dashboard,
)

router = APIRouter()


@router.get("/professor")
def professor_dashboard(user=Depends(require_role(REVIEW_ROLES))):
    db = SessionLocal()
    try:
        return get_professor_dashboard(db, owner_id=int(user["id"]))
    finally:
        db.close()


@router.get("/student")
def student_dashboard(user=Depends(get_current_user)):
    role = (user.get("role") or "").lower()
    if role != ROLE_STUDENT:
        return {"error": "Student role required", "results": []}

    student_key = user.get("email") or str(user.get("id") or "")
    db = SessionLocal()
    try:
        return get_student_dashboard(db, student_key=student_key)
    finally:
        db.close()


@router.get("/review-stats")
def dashboard_review_stats(_user=Depends(get_current_user)):
    db = SessionLocal()
    try:
        return get_review_stats(db)
    finally:
        db.close()
