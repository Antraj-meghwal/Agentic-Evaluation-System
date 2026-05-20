import json
import os

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

from utils.image_utils import encode_image


load_dotenv()


class CriticAgent:

    def __init__(self):

        self.client = InferenceClient(
            provider="hf-inference",
            api_key=os.getenv("HF_TOKEN")
        )

        self.model = (
            "Qwen/Qwen2-VL-7B-Instruct"
        )

    def review(
        self,
        grading_context: dict,
        grader_output: dict
    ) -> dict:

        prompt = f"""
You are a strict academic grading critic.

Your task:
Review the grader's evaluation carefully.

Detect:
- rubric violations
- unsupported scoring
- weak reasoning
- inconsistent grading

Rubric:
{json.dumps(grading_context["rubric"], indent=2)}

OCR Transcript:
{grading_context["ocr_text"]}

Original Grader Output:
{json.dumps(grader_output, indent=2)}

Return ONLY valid JSON.

Required JSON format:
{{
  "approved": bool,
  "requires_human_review": bool,
  "corrected_score": int,
  "confidence": float,
  "critic_feedback": str
}}
"""

        image_base64 = encode_image(
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
                                    "url":
                                    (
                                        "data:image/png;base64,"
                                        f"{image_base64}"
                                    )
                                }
                            }
                        ]
                    }
                ],

                max_tokens=500
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