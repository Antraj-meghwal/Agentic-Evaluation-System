"""Bridge EXTRACT pipeline → Tribunal agents → PostgreSQL grading_results."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import UUID

from db.session import SessionLocal
from models.batch import Batch, BatchStatus
from models.grading_result import GradingResult, ResolutionStatus
from models.question_crop import CropStatus, QuestionCrop
from models.submission import Submission, SubmissionStatus
from pipeline.tribunal.coordinator import resolve_tribunal_decision
from pipeline.verify.escalation_engine import should_escalate_to_human
from services.pipeline.extract.runner import run_extract_phase
from services.pipeline.schemas import GradingContext
from services.plagiarism_service import detect_similar_pairs, detect_visual_plagiarism
from services.rag_helper import retrieve_similar_answers, store_graded_answer
from services.tribunal_agents import run_critic, run_grader


def _default_rubric_paths() -> tuple[Path, Path]:
    root = Path(__file__).resolve().parents[2]
    return (
        root / "examples" / "sample_rubric.json",
        Path(__file__).resolve().parents[1] / "data" / "rubrics" / "sample_rubric.json",
    )


def resolve_rubric_path() -> str | None:
    primary, fallback = _default_rubric_paths()
    if primary.exists():
        return str(primary)
    if fallback.exists():
        return str(fallback)
    return None


def build_tribunal_context(ctx: GradingContext, upload_id: int) -> dict[str, Any]:
    q = ctx.question
    rubric_q = {
        "q_id": q.id,
        "max_points": int(q.max_points),
        "content_type": (q.question_type.value or "text").upper(),
        "bypass_ocr": ctx.crop.bypass_ocr,
        "criteria": [
            {
                "id": c.id,
                "description": c.description,
                "points": int(c.max_points),
            }
            for c in q.criteria
        ],
    }
    return {
        "student_id": f"upload-{upload_id}",
        "question_id": q.id,
        "rubric": rubric_q,
        "ocr_text": ctx.ocr.transcript if ctx.ocr else "",
        "crop_image_path": ctx.crop.image_path,
        "content_type": rubric_q["content_type"],
        "bypass_ocr": ctx.crop.bypass_ocr,
        "similar_answers": [],
        "upload_id": upload_id,
    }


def persist_tribunal_result(
    db,
    *,
    upload_id: int,
    batch: Batch,
    submission: Submission,
    ctx: GradingContext,
    grader_output: dict,
    critic_output: dict,
    resolution: dict,
    escalate: bool,
    escalation_reasons: list[str],
    plagiarism_flags: list[dict],
) -> GradingResult:
    crop = QuestionCrop(
        submission_id=submission.id,
        question_id=ctx.question.id,
        page_number=ctx.crop.page_index,
        crop_image_path=ctx.crop.image_path,
        ocr_text=ctx.ocr.transcript if ctx.ocr else "",
        status=CropStatus.GRADED,
    )
    db.add(crop)
    db.flush()

    grading_result = GradingResult(
        question_crop_id=crop.id,
        final_score=int(resolution["final_score"]),
        max_score=int(grader_output.get("max_score", ctx.question.max_points)),
        confidence_score=float(grader_output.get("confidence", 0.0)),
        resolution_status=resolution["resolution_status"],
        requires_human_review=resolution["requires_human_review"] or escalate,
        grader_output=grader_output,
        critic_output=critic_output,
        coordinator_output={
            "upload_id": upload_id,
            "escalation_reasons": escalation_reasons,
            "plagiarism_flags": plagiarism_flags,
        },
        final_feedback=grader_output.get("feedback", ""),
    )
    db.add(grading_result)
    return grading_result


def run_tribunal_for_upload(
    upload_id: int,
    file_path: str,
    *,
    rubric_path: str | None = None,
    rubric_json: dict | None = None,
    owner_email: str = "system",
) -> dict[str, Any]:
    """
    Full pipeline: EXTRACT → Tribunal (grader + critic) → persist → plagiarism scan.
    """
    extract = run_extract_phase(
        upload_id=upload_id,
        file_path=file_path,
        rubric_path=rubric_path,
        rubric_json=rubric_json,
    )

    db = SessionLocal()
    results: list[dict[str, Any]] = []
    transcripts: dict[str, str] = {}
    crop_paths: dict[str, str] = {}

    try:
        rubric_path_str = rubric_path or resolve_rubric_path() or ""
        batch = Batch(
            exam_name=f"upload-{upload_id}",
            uploaded_by=owner_email,
            pdf_path=file_path,
            rubric_path=rubric_path_str,
            status=BatchStatus.PROCESSING,
        )
        db.add(batch)
        db.flush()

        submission = Submission(
            batch_id=batch.id,
            student_id=f"upload-{upload_id}",
            original_pdf_path=file_path,
            status=SubmissionStatus.CROPPED,
        )
        db.add(submission)
        db.flush()

        from pipeline.tribunal.graph import app as tribunal_graph
        
        for ctx in extract.contexts:
            tribunal_ctx = build_tribunal_context(ctx, upload_id)
            ocr_text = tribunal_ctx.get("ocr_text", "")
            tribunal_ctx["similar_answers"] = retrieve_similar_answers(
                ctx.question.id,
                ocr_text,
            )
            transcripts[ctx.question.id] = ocr_text
            crop_paths[ctx.question.id] = ctx.crop.image_path

            # Execute LangGraph
            initial_state = {"tribunal_ctx": tribunal_ctx}
            final_state = tribunal_graph.invoke(initial_state)

            grader_output = final_state.get("grader_output", {})
            critic_output = final_state.get("critic_output", {})
            resolution = final_state.get("resolution", {})
            escalate = final_state.get("escalate", False)
            escalation_reasons = final_state.get("escalation_reasons", [])

            grading_result = persist_tribunal_result(
                db,
                upload_id=upload_id,
                batch=batch,
                submission=submission,
                ctx=ctx,
                grader_output=grader_output,
                critic_output=critic_output,
                resolution=resolution,
                escalate=escalate,
                escalation_reasons=escalation_reasons,
                plagiarism_flags=[],
            )

            store_graded_answer(
                crop_id=str(crop.id),
                question_id=ctx.question.id,
                answer_text=ocr_text or grading_result.final_feedback or "",
                final_score=grading_result.final_score,
            )

            results.append(
                {
                    "grading_result_id": str(grading_result.id),
                    "question_id": ctx.question.id,
                    "score": grading_result.final_score,
                    "max_score": grading_result.max_score,
                    "confidence": grading_result.confidence_score,
                    "requires_human_review": grading_result.requires_human_review,
                    "feedback": grading_result.final_feedback,
                    "criteria_breakdown": grader_output.get("criteria_breakdown", []),
                    "resolution_status": grading_result.resolution_status.value,
                }
            )

        # ── Text-based plagiarism (transcript similarity) ──────────────
        plagiarism_flags = detect_similar_pairs(transcripts)

        # ── CLIP visual plagiarism (image crop similarity) ────────────
        visual_flags = detect_visual_plagiarism(crop_paths)
        plagiarism_flags.extend(visual_flags)

        # ── Persist flags into grading results ────────────────────────
        if plagiarism_flags:
            for item in results:
                gr = (
                    db.query(GradingResult)
                    .filter(GradingResult.id == UUID(item["grading_result_id"]))
                    .first()
                )
                if gr and gr.coordinator_output:
                    out = dict(gr.coordinator_output)
                    out["plagiarism_flags"] = plagiarism_flags
                    gr.coordinator_output = out
                    if any(
                        f["question_a"] == item["question_id"]
                        or f["question_b"] == item["question_id"]
                        for f in plagiarism_flags
                    ):
                        gr.requires_human_review = True

        batch.status = BatchStatus.COMPLETED
        submission.status = SubmissionStatus.GRADED
        db.commit()

        return {
            "upload_id": upload_id,
            "batch_id": str(batch.id),
            "status": "graded",
            "questions_graded": len(results),
            "plagiarism_flags": plagiarism_flags,
            "results": results,
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
