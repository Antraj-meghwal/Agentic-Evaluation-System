"""Gradebook export service — CSV, Canvas-compatible CSV, and JSON formats.

Aggregates grading results for a batch or upload and produces downloadable
exports that can be imported into Canvas, Moodle, Blackboard, or used as
standalone gradebook records.
"""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from models.batch import Batch
from models.grading_result import GradingResult
from models.question_crop import QuestionCrop
from models.review_action import ReviewAction
from models.submission import Submission


# ──────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────

def _fetch_results_for_upload(db: Session, upload_id: int) -> list[dict[str, Any]]:
    """Gather grading results linked to a specific upload_id via coordinator_output."""
    rows = db.query(GradingResult).all()
    items: list[dict[str, Any]] = []

    for gr in rows:
        meta = gr.coordinator_output or {}
        if int(meta.get("upload_id", -1)) != upload_id:
            continue

        crop = (
            db.query(QuestionCrop)
            .filter(QuestionCrop.id == gr.question_crop_id)
            .first()
        )

        # Check for human review overrides
        review = (
            db.query(ReviewAction)
            .filter(ReviewAction.grading_result_id == gr.id)
            .order_by(ReviewAction.created_at.desc())
            .first()
        )

        final_score = gr.final_score
        review_status = "AI Graded"
        reviewer = ""

        if review:
            if review.action_type.value == "OVERRIDDEN" and review.updated_score is not None:
                final_score = review.updated_score
                review_status = "Human Overridden"
            elif review.action_type.value == "APPROVED":
                review_status = "Human Approved"
            elif review.action_type.value == "FLAGGED":
                review_status = "Flagged"
            reviewer = review.reviewer_id

        items.append({
            "grading_result_id": str(gr.id),
            "question_id": crop.question_id if crop else "unknown",
            "student_id": meta.get("upload_id", upload_id),
            "score": final_score,
            "max_score": gr.max_score,
            "percentage": round((final_score / gr.max_score) * 100, 2) if gr.max_score else 0,
            "confidence": round(gr.confidence_score, 3) if gr.confidence_score else None,
            "resolution_status": gr.resolution_status.value,
            "review_status": review_status,
            "reviewer": reviewer,
            "feedback": gr.final_feedback or "",
            "requires_human_review": gr.requires_human_review,
            "plagiarism_flags": meta.get("plagiarism_flags", []),
            "escalation_reasons": meta.get("escalation_reasons", []),
            "graded_at": gr.created_at.isoformat() if gr.created_at else "",
        })

    return items


def _fetch_results_for_batch(db: Session, batch_id: str) -> list[dict[str, Any]]:
    """Gather grading results for all submissions in a batch."""
    batch = db.query(Batch).filter(Batch.id == batch_id).first()
    if not batch:
        return []

    submissions = (
        db.query(Submission)
        .filter(Submission.batch_id == batch.id)
        .all()
    )

    items: list[dict[str, Any]] = []
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

            review = (
                db.query(ReviewAction)
                .filter(ReviewAction.grading_result_id == gr.id)
                .order_by(ReviewAction.created_at.desc())
                .first()
            )

            final_score = gr.final_score
            review_status = "AI Graded"
            reviewer = ""

            if review:
                if review.action_type.value == "OVERRIDDEN" and review.updated_score is not None:
                    final_score = review.updated_score
                    review_status = "Human Overridden"
                elif review.action_type.value == "APPROVED":
                    review_status = "Human Approved"
                elif review.action_type.value == "FLAGGED":
                    review_status = "Flagged"
                reviewer = review.reviewer_id

            meta = gr.coordinator_output or {}

            items.append({
                "grading_result_id": str(gr.id),
                "question_id": crop.question_id,
                "student_id": sub.student_id,
                "score": final_score,
                "max_score": gr.max_score,
                "percentage": round((final_score / gr.max_score) * 100, 2) if gr.max_score else 0,
                "confidence": round(gr.confidence_score, 3) if gr.confidence_score else None,
                "resolution_status": gr.resolution_status.value,
                "review_status": review_status,
                "reviewer": reviewer,
                "feedback": gr.final_feedback or "",
                "requires_human_review": gr.requires_human_review,
                "plagiarism_flags": meta.get("plagiarism_flags", []),
                "escalation_reasons": meta.get("escalation_reasons", []),
                "graded_at": gr.created_at.isoformat() if gr.created_at else "",
            })

    return items


def _build_summary(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute aggregate statistics for a set of grading results."""
    if not items:
        return {
            "total_questions": 0,
            "total_score": 0,
            "total_max_score": 0,
            "overall_percentage": 0,
            "avg_confidence": 0,
            "needs_review_count": 0,
            "plagiarism_count": 0,
        }

    total_score = sum(i["score"] for i in items)
    total_max = sum(i["max_score"] for i in items)
    confidences = [i["confidence"] for i in items if i["confidence"] is not None]
    plag_count = sum(1 for i in items if i["plagiarism_flags"])

    return {
        "total_questions": len(items),
        "total_score": total_score,
        "total_max_score": total_max,
        "overall_percentage": round((total_score / total_max) * 100, 2) if total_max else 0,
        "avg_confidence": round(sum(confidences) / len(confidences), 3) if confidences else 0,
        "needs_review_count": sum(1 for i in items if i["requires_human_review"]),
        "plagiarism_count": plag_count,
    }


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def export_gradebook_csv(
    db: Session,
    *,
    upload_id: int | None = None,
    batch_id: str | None = None,
) -> str:
    """
    Generate a standard gradebook CSV string.

    Columns: Student ID, Question, Score, Max Score, %, Confidence,
             Status, Review Status, Feedback, Graded At
    """
    if upload_id is not None:
        items = _fetch_results_for_upload(db, upload_id)
    elif batch_id is not None:
        items = _fetch_results_for_batch(db, batch_id)
    else:
        raise ValueError("Either upload_id or batch_id is required")

    buf = io.StringIO()
    writer = csv.writer(buf)

    # Header
    writer.writerow([
        "Student ID",
        "Question",
        "Score",
        "Max Score",
        "Percentage",
        "Confidence",
        "Resolution Status",
        "Review Status",
        "Reviewer",
        "Feedback",
        "Needs Human Review",
        "Plagiarism Flagged",
        "Graded At",
    ])

    for item in items:
        writer.writerow([
            item["student_id"],
            item["question_id"],
            item["score"],
            item["max_score"],
            f'{item["percentage"]}%',
            item["confidence"] if item["confidence"] is not None else "",
            item["resolution_status"],
            item["review_status"],
            item["reviewer"],
            item["feedback"],
            "Yes" if item["requires_human_review"] else "No",
            "Yes" if item["plagiarism_flags"] else "No",
            item["graded_at"],
        ])

    # Summary rows
    summary = _build_summary(items)
    writer.writerow([])
    writer.writerow(["--- Summary ---"])
    writer.writerow(["Total Questions", summary["total_questions"]])
    writer.writerow(["Total Score", f'{summary["total_score"]}/{summary["total_max_score"]}'])
    writer.writerow(["Overall Percentage", f'{summary["overall_percentage"]}%'])
    writer.writerow(["Avg Confidence", summary["avg_confidence"]])
    writer.writerow(["Needs Review", summary["needs_review_count"]])
    writer.writerow(["Plagiarism Flags", summary["plagiarism_count"]])

    return buf.getvalue()


def export_canvas_csv(
    db: Session,
    *,
    upload_id: int | None = None,
    batch_id: str | None = None,
) -> str:
    """
    Generate a Canvas-compatible CSV.

    Canvas import format requires:
      Student, ID, SIS User ID, SIS Login ID, Section, <Assignment Name>
    We map each question to an assignment column.
    """
    if upload_id is not None:
        items = _fetch_results_for_upload(db, upload_id)
    elif batch_id is not None:
        items = _fetch_results_for_batch(db, batch_id)
    else:
        raise ValueError("Either upload_id or batch_id is required")

    # Group by student → question → score
    students: dict[str, dict[str, int]] = {}
    questions: dict[str, int] = {}  # question_id → max_score

    for item in items:
        sid = str(item["student_id"])
        qid = item["question_id"]
        students.setdefault(sid, {})[qid] = item["score"]
        questions[qid] = item["max_score"]

    sorted_questions = sorted(questions.keys())

    buf = io.StringIO()
    writer = csv.writer(buf)

    # Canvas header: Student, ID, then one column per question (with points possible)
    header = ["Student", "ID"]
    for qid in sorted_questions:
        header.append(f"Q{qid} (Points Possible: {questions[qid]})")
    writer.writerow(header)

    # Points possible row (Canvas convention)
    points_row = ["    Points Possible", ""]
    for qid in sorted_questions:
        points_row.append(questions[qid])
    writer.writerow(points_row)

    # Student rows
    for sid in sorted(students.keys()):
        row = [sid, sid]
        for qid in sorted_questions:
            row.append(students[sid].get(qid, ""))
        writer.writerow(row)

    return buf.getvalue()


def export_gradebook_json(
    db: Session,
    *,
    upload_id: int | None = None,
    batch_id: str | None = None,
) -> dict[str, Any]:
    """
    Generate a full JSON gradebook with per-question results and summary.
    """
    if upload_id is not None:
        items = _fetch_results_for_upload(db, upload_id)
    elif batch_id is not None:
        items = _fetch_results_for_batch(db, batch_id)
    else:
        raise ValueError("Either upload_id or batch_id is required")

    summary = _build_summary(items)

    return {
        "export_format": "gradeops_gradebook_v1",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "upload_id": upload_id,
        "batch_id": batch_id,
        "summary": summary,
        "results": items,
    }
