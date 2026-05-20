import json
import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from pipeline.tribunal.base_grader import (
    BaseGraderProvider
)

from utils.image_utils import encode_image

load_dotenv()


class HuggingFaceVLMGrader(
    BaseGraderProvider
):

    def __init__(self):

        self.client = InferenceClient(
            provider="hf-inference",
            api_key=os.getenv("HF_TOKEN")
        )

        self.model = (
            "Qwen/Qwen2-VL-7B-Instruct"
        )

    def grade(
    self,
    grading_context: dict
) -> dict:

    rubric = grading_context["rubric"]

    prompt = f"""
You are an expert university examiner.

Grade the student's answer STRICTLY
according to the rubric.

Use the previously graded answers ONLY
as consistency references.
Do NOT copy scores blindly.

Return ONLY valid JSON.

Rubric:
{json.dumps(rubric, indent=2)}

OCR Transcript:
{grading_context["ocr_text"]}

Similar Previously Graded Answers:
{json.dumps(grading_context["similar_answers"], indent=2)}

Required JSON format:
{{
  "score": int,
  "max_score": int,
  "confidence": float,
  "feedback": str,
  "criteria_breakdown": [
    {{
      "criterion_id": str,
      "awarded_points": int,
      "max_points": int,
      "reasoning": str
    }}
  ]
}}
"""

    image_path = (
        grading_context["crop_image_path"]
    )

    completion = (
        self.client.chat.completions.create(
            model=self.model,

            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": (
                                    "data:image/png;base64,"
                                    f"{encode_image(image_path)}"
                                )
                            }
                        }
                    ]
                }
            ],

            max_tokens=800
        )
    )

    raw_output = (
        completion
        .choices[0]
        .message
        .content
    )

    cleaned_output = (
        raw_output
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    return json.loads(cleaned_output)