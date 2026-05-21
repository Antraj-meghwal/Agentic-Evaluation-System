"""Dashboard aggregates for professor and student UIs."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from models.grading_result import GradingResult
from models.question_crop import QuestionCrop
from models.review_action import ReviewAction, ReviewActionType
from models.submission import Submission
from models.upload_model import UploadedFile


def _grading_results_for_upload_ids(db: Session, upload_ids: list[int]) -> list[GradingResult]:
    if not upload_ids:
        return []
    rows = db.query(GradingResult).all()
    matched: list[GradingResult] = []
    id_set = set(upload_ids)
    for gr in rows:
        meta = gr.coordinator_output or {}
        if int(meta.get("upload_id", -1)) in id_set:
            matched.append(gr)
    return matched


def get_professor_dashboard(db: Session, owner_id: int) -> dict[str, Any]:
    uploads = (
        db.query(UploadedFile)
        .filter(UploadedFile.owner_id == owner_id)
        .order_by(UploadedFile.created_at.desc())
        .all()
    )
    upload_ids = [u.id for u in uploads]
    results = _grading_results_for_upload_ids(db, upload_ids)

    pending_reviews = sum(1 for r in results if r.requires_human_review)
    total_score = sum(r.final_score for r in results)
    total_max = sum(r.max_score for r in results)
    avg_pct = round((total_score / total_max) * 100) if total_max else 0

    recent = [
        {
            "upload_id": u.id,
            "filename": u.filename,
            "status": u.status,
            "created_at": u.created_at.isoformat() if u.created_at else "",
        }
        for u in uploads[:5]
    ]

    return {
        "upload_count": len(uploads),
        "pending_reviews": pending_reviews,
        "total_graded": len(results),
        "avg_class_score_pct": avg_pct,
        "recent_uploads": recent,
    }


def get_student_dashboard(db: Session, student_key: str) -> dict[str, Any]:
    """
    Return graded work for a student.

    Matches submission.student_id against the student's email or numeric id.
    """
    submissions = (
        db.query(Submission)
        .filter(Submission.student_id.in_([student_key, str(student_key)]))
        .all()
    )

    graded_items: list[dict[str, Any]] = []
    total_score = 0
    total_max = 0

    for sub in submissions:
        crops = (
            db.query(QuestionCrop)
            .filter(QuestionCrop.submission_id == sub.id)
            .all()
        )
        for crop in crops:
            if not crop.grading_result:
                continue
            gr = crop.grading_result
            total_score += gr.final_score
            total_max += gr.max_score
            graded_items.append(
                {
                    "submission_id": str(sub.id),
                    "question_id": crop.question_id,
                    "score": gr.final_score,
                    "max_score": gr.max_score,
                    "feedback": gr.final_feedback,
                    "requires_human_review": gr.requires_human_review,
                    "graded_at": gr.created_at.isoformat() if gr.created_at else "",
                }
            )

    avg_pct = round((total_score / total_max) * 100) if total_max else 0

    return {
        "assignments_graded": len({i["submission_id"] for i in graded_items}) or len(graded_items),
        "total_questions_graded": len(graded_items),
        "avg_score_pct": avg_pct,
        "pending_count": sum(1 for i in graded_items if i["requires_human_review"]),
        "results": graded_items[:20],
    }


def get_review_stats(db: Session) -> dict[str, int]:
    pending = (
        db.query(GradingResult)
        .filter(GradingResult.requires_human_review.is_(True))
        .count()
    )
    total = db.query(GradingResult).count()
    overrides = (
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
        "overrides": overrides,
        "low_confidence": low_confidence,
    }
