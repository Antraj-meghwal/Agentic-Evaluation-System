"""EXTRACT phase: Nougat / Qwen-VL OCR via Hugging Face."""

from __future__ import annotations

from pathlib import Path

from services.pipeline.config import MODELS
from services.pipeline.hf_client import get_hf_client
from services.pipeline.schemas import OcrResult, QuestionCrop

OCR_PROMPT = """You are an academic OCR system for handwritten exam answers.

Transcribe ALL visible handwriting and mathematical notation from this image.
Preserve line breaks. Use LaTeX for formulas when possible.

Return STRICT JSON only:
{
  "transcript": "full transcription",
  "confidence": 0.0 to 1.0,
  "has_diagram": true or false
}
"""


def extract_transcript(crop: QuestionCrop) -> OcrResult:
    if crop.bypass_ocr:
        return OcrResult(
            question_id=crop.question_id,
            transcript="",
            model_id="bypass",
            confidence=1.0,
        )

    client = get_hf_client()
    model_id = MODELS.ocr_vlm
    response = client.image_to_text(
        crop.image_path,
        OCR_PROMPT,
        model_id,
    )

    parsed = response.get("parsed") or {}
    transcript = parsed.get("transcript") or response.get("text", "")
    confidence = float(parsed.get("confidence", 0.7))

    # Nougat fallback when primary OCR confidence is low
    if confidence < 0.5 and MODELS.ocr_fallback:
        fallback = client.image_to_text(
            crop.image_path,
            OCR_PROMPT,
            MODELS.ocr_fallback,
        )
        fb_parsed = fallback.get("parsed") or {}
        fb_conf = float(fb_parsed.get("confidence", 0.0))
        if fb_conf > confidence:
            response = fallback
            parsed = fb_parsed
            transcript = parsed.get("transcript") or fallback.get("text", transcript)
            confidence = fb_conf
            model_id = MODELS.ocr_fallback

    return OcrResult(
        question_id=crop.question_id,
        transcript=transcript.strip(),
        model_id=model_id,
        confidence=confidence,
        raw_response=response,
    )


def should_bypass_ocr(crop: QuestionCrop, ocr: OcrResult) -> bool:
    """Flag diagram-heavy answers for raw-image Tribunal path."""
    raw = ocr.raw_response or {}
    parsed = raw.get("parsed") or {}
    if parsed.get("has_diagram"):
        return True
    if len(ocr.transcript.strip()) < 20:
        return True
    return crop.bypass_ocr
