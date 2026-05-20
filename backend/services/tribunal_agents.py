"""Tribunal grader/critic using shared HF client (supports PIPELINE_DRY_RUN)."""

from __future__ import annotations

import json

from services.pipeline.config import MODELS, PIPELINE_DRY_RUN
from services.pipeline.hf_client import get_hf_client


def _mock_grader(grading_context: dict) -> dict:
    rubric = grading_context["rubric"]
    max_score = int(rubric.get("max_points", 10))
    return {
        "score": max(0, max_score - 2),
        "max_score": max_score,
        "confidence": 0.55,
        "feedback": "Mock tribunal grade (set HF_TOKEN or use PIPELINE_DRY_RUN=false).",
        "criteria_breakdown": [
            {
                "criterion_id": c.get("id", f"c{i}"),
                "awarded_points": max(0, int(c.get("points", 1)) - 1),
                "max_points": int(c.get("points", 1)),
                "reasoning": "Dry-run partial credit.",
            }
            for i, c in enumerate(rubric.get("criteria", []))
        ],
    }


def _mock_critic(grader_output: dict) -> dict:
    score = grader_output.get("score", 0)
    return {
        "approved": grader_output.get("confidence", 1) >= 0.8,
        "requires_human_review": grader_output.get("confidence", 1) < 0.65,
        "corrected_score": score,
        "confidence": 0.7,
        "critic_feedback": "Mock critic review.",
    }


def run_grader(grading_context: dict) -> dict:
    if PIPELINE_DRY_RUN:
        return _mock_grader(grading_context)

    rubric = grading_context["rubric"]
    prompt = f"""You are an expert university examiner.
Grade the student's answer STRICTLY according to the rubric.
Return ONLY valid JSON.

Rubric:
{json.dumps(rubric, indent=2)}

OCR Transcript:
{grading_context.get("ocr_text", "")}

Required JSON format:
{{
  "score": int,
  "max_score": int,
  "confidence": float,
  "feedback": str,
  "criteria_breakdown": [
    {{"criterion_id": str, "awarded_points": int, "max_points": int, "reasoning": str}}
  ]
}}
"""
    client = get_hf_client()
    response = client.image_to_text(
        grading_context["crop_image_path"],
        prompt,
        MODELS.grader_vlm,
    )
    parsed = response.get("parsed") or {}
    max_score = int(parsed.get("max_score") or rubric.get("max_points", 10))
    return {
        "score": int(parsed.get("score", 0)),
        "max_score": max_score,
        "confidence": float(parsed.get("confidence", 0.7)),
        "feedback": parsed.get("feedback", response.get("text", "")),
        "criteria_breakdown": parsed.get("criteria_breakdown", []),
    }


def run_critic(grading_context: dict, grader_output: dict) -> dict:
    if PIPELINE_DRY_RUN:
        return _mock_critic(grader_output)

    prompt = f"""You are a strict academic grading critic.
Review the grader's evaluation. Return ONLY valid JSON.

Rubric:
{json.dumps(grading_context["rubric"], indent=2)}

OCR Transcript:
{grading_context.get("ocr_text", "")}

Grader Output:
{json.dumps(grader_output, indent=2)}

Required JSON format:
{{
  "approved": bool,
  "requires_human_review": bool,
  "corrected_score": int,
  "confidence": float,
  "critic_feedback": str
}}
"""
    client = get_hf_client()
    response = client.text_generation(prompt, MODELS.critic_llm, max_tokens=512)
    text = response.get("text", "")
    try:
        from services.pipeline.hf_client import _parse_json_from_text

        parsed = _parse_json_from_text(text)
    except Exception:
        parsed = {
            "approved": True,
            "requires_human_review": False,
            "corrected_score": grader_output.get("score", 0),
            "confidence": 0.6,
            "critic_feedback": text[:500],
        }
    return {
        "approved": bool(parsed.get("approved", True)),
        "requires_human_review": bool(parsed.get("requires_human_review", False)),
        "corrected_score": int(parsed.get("corrected_score", grader_output.get("score", 0))),
        "confidence": float(parsed.get("confidence", 0.6)),
        "critic_feedback": parsed.get("critic_feedback", ""),
    }
