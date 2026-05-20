"""Legacy single-shot VLM grading — delegates to shared HF client."""

from services.pipeline.config import MODELS
from services.pipeline.hf_client import get_hf_client


def grade_answer_sheet(image_path: str, rubric: str) -> dict:
    prompt = f"""
You are an academic evaluator.

Grade the student's handwritten answer sheet using the rubric.

RUBRIC:
{rubric}

Return STRICT JSON:
{{
  "score": number,
  "feedback": "short feedback",
  "confidence": number
}}
"""
    client = get_hf_client()
    response = client.image_to_text(
        image_path,
        prompt,
        MODELS.grader_vlm,
    )
    if response.get("parsed"):
        return response["parsed"]
    return {"raw": response.get("text"), "model_id": response.get("model_id")}
