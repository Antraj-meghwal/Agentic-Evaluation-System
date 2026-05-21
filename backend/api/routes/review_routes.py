from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from db.session import SessionLocal
from core.constants import REVIEW_ROLES
from dependencies import get_current_user, require_role
from models.grading_result import GradingResult
from models.question_crop import QuestionCrop
from models.review_action import ReviewAction, ReviewActionType
from schemas.review_schema import ReviewDecisionSchema

router = APIRouter()


def _image_url(path: str | None) -> str | None:
    if not path:
        return None
    return f"/{path.lstrip('/')}"


def _serialize_review_item(db, item: GradingResult) -> dict:
    crop = (
        db.query(QuestionCrop)
        .filter(QuestionCrop.id == item.question_crop_id)
        .first()
    )
    meta = item.coordinator_output or {}
    grader = item.grader_output or {}
    critic = item.critic_output or {}
    return {
        "grading_result_id": str(item.id),
        "upload_id": meta.get("upload_id"),
        "question_id": crop.question_id if crop else None,
        "score": item.final_score,
        "max_score": item.max_score,
        "confidence": item.confidence_score,
        "feedback": item.final_feedback,
        "critic_feedback": critic.get("critic_feedback"),
        "resolution_status": item.resolution_status.value,
        "requires_human_review": item.requires_human_review,
        "escalation_reasons": meta.get("escalation_reasons", []),
        "plagiarism_flags": meta.get("plagiarism_flags", []),
        "criteria_breakdown": grader.get("criteria_breakdown", []),
        "crop_image_url": _image_url(crop.crop_image_path if crop else None),
        "ocr_text": crop.ocr_text if crop else None,
    }


@router.get("/review-queue")
def get_review_queue(_user=Depends(require_role(REVIEW_ROLES))):
    db = SessionLocal()
    try:
        review_items = (
            db.query(GradingResult)
            .filter(GradingResult.requires_human_review.is_(True))
            .order_by(GradingResult.created_at.desc())
            .all()
        )
        return [_serialize_review_item(db, item) for item in review_items]
    finally:
        db.close()


@router.get("/stats")
def review_stats(_user=Depends(require_role(REVIEW_ROLES))):
    db = SessionLocal()
    try:
        pending = (
            db.query(GradingResult)
            .filter(GradingResult.requires_human_review.is_(True))
            .count()
        )
        total = db.query(GradingResult).count()
        reviewed = (
            db.query(ReviewAction)
            .filter(ReviewAction.action_type == ReviewActionType.OVERRIDDEN)
            .count()
        )
        low_confidence = (
            db.query(GradingResult)
            .filter(GradingResult.confidence_score < 0.6)
            .count()
        )
        return {
            "pending_reviews": pending,
            "total_graded": total,
            "overrides": reviewed,
            "low_confidence": low_confidence,
        }
    finally:
        db.close()


@router.post("/approve/{grading_result_id}")
def approve_grade(grading_result_id: str, _user=Depends(require_role(REVIEW_ROLES))):
    db = SessionLocal()
    try:
        gr = (
            db.query(GradingResult)
            .filter(GradingResult.id == UUID(grading_result_id))
            .first()
        )
        if not gr:
            raise HTTPException(status_code=404, detail="Result not found")

        gr.requires_human_review = False
        db.add(
            ReviewAction(
                grading_result_id=gr.id,
                reviewer_id=str(_user.get("id") or _user.get("sub")),
                action_type=ReviewActionType.APPROVED,
                original_score=gr.final_score,
                updated_score=gr.final_score,
                review_notes="Approved via TA dashboard",
            )
        )
        db.commit()
        return {"message": "Approved", "grading_result_id": grading_result_id}
    finally:
        db.close()


@router.post("/override/{grading_result_id}")
def override_grade(
    grading_result_id: str,
    review_data: ReviewDecisionSchema,
    user=Depends(require_role(REVIEW_ROLES)),
):
    db = SessionLocal()
    try:
        grading_result = (
            db.query(GradingResult)
            .filter(GradingResult.id == UUID(grading_result_id))
            .first()
        )
        if not grading_result:
            raise HTTPException(status_code=404, detail="Result not found")

        original_score = grading_result.final_score
        grading_result.final_score = review_data.updated_score
        grading_result.requires_human_review = False

        reviewer_id = review_data.reviewer_id or str(
            user.get("id") or user.get("sub") or "unknown"
        )

        review_action = ReviewAction(
            grading_result_id=grading_result.id,
            reviewer_id=reviewer_id,
            action_type=ReviewActionType.OVERRIDDEN,
            original_score=original_score,
            updated_score=review_data.updated_score,
            review_notes=review_data.review_notes,
        )

        db.add(review_action)
        db.commit()
        return {"message": "Override successful"}
    finally:
        db.close()
