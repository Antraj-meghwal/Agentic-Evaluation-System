"""Unified Hugging Face Inference client for all pipeline models."""

from __future__ import annotations

import base64
import json
import logging
import re
from pathlib import Path
from typing import Any

from services.pipeline.config import HF_TOKEN, PIPELINE_DRY_RUN

logger = logging.getLogger(__name__)


def _encode_image(path: str | Path) -> str:
    data = Path(path).read_bytes()
    return base64.b64encode(data).decode("utf-8")


def _parse_json_from_text(text: str) -> dict[str, Any]:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group())
        raise


class HuggingFaceClient:
    """Wraps huggingface_hub InferenceClient with dry-run fallback."""

    def __init__(self, token: str | None = None):
        self.token = token or HF_TOKEN
        self._client = None
        if self.token and not PIPELINE_DRY_RUN:
            from huggingface_hub import InferenceClient

            self._client = InferenceClient(token=self.token)

    @property
    def available(self) -> bool:
        return self._client is not None

    def image_to_text(
        self,
        image_path: str | Path,
        prompt: str,
        model_id: str,
    ) -> dict[str, Any]:
        """VLM call: image + text prompt → structured or raw response."""
        if PIPELINE_DRY_RUN or not self.available:
            return self._mock_vlm_response(image_path, prompt, model_id)

        image_b64 = _encode_image(image_path)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image_b64},
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        try:
            out = self._client.chat.completions.create(
                model=model_id,
                messages=messages,
                max_tokens=1024,
            )
            text = out.choices[0].message.content
            return {"text": text, "model_id": model_id, "parsed": _parse_json_from_text(text)}
        except Exception as exc:
            logger.warning("HF VLM failed (%s), using text_generation fallback", exc)
            return self._legacy_inference(image_path, prompt, model_id)

    def text_generation(
        self,
        prompt: str,
        model_id: str,
        max_tokens: int = 512,
    ) -> dict[str, Any]:
        if PIPELINE_DRY_RUN or not self.available:
            return {
                "text": '{"agrees": true, "critique": "Dry-run mode.", "suggested_score": null}',
                "model_id": model_id,
            }
        out = self._client.text_generation(
            prompt,
            model=model_id,
            max_new_tokens=max_tokens,
        )
        text = out if isinstance(out, str) else str(out)
        return {"text": text, "model_id": model_id}

    def _legacy_inference(
        self,
        image_path: str | Path,
        prompt: str,
        model_id: str,
    ) -> dict[str, Any]:
        import requests
        from services.pipeline.config import HF_API_URL

        payload = {
            "inputs": {
                "image": _encode_image(image_path),
                "text": prompt,
            }
        }
        headers = {"Authorization": f"Bearer {self.token}"}
        url = f"{HF_API_URL}/models/{model_id}"
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and data:
            text = data[0].get("generated_text", str(data[0]))
        elif isinstance(data, dict):
            text = data.get("generated_text") or data.get("text") or str(data)
        else:
            text = str(data)
        parsed = None
        try:
            parsed = _parse_json_from_text(text)
        except json.JSONDecodeError:
            pass
        return {"text": text, "model_id": model_id, "parsed": parsed, "raw": data}

    @staticmethod
    def _mock_vlm_response(
        image_path: str | Path,
        prompt: str,
        model_id: str,
    ) -> dict[str, Any]:
        name = Path(image_path).name
        return {
            "text": (
                f'{{"transcript": "[mock OCR for {name}]", '
                f'"confidence": 0.85, "notes": "Set HF_TOKEN or disable PIPELINE_DRY_RUN"}}'
            ),
            "model_id": model_id,
            "parsed": {
                "transcript": f"[mock OCR for {name}]",
                "confidence": 0.85,
            },
        }


_hf_client: HuggingFaceClient | None = None


def get_hf_client() -> HuggingFaceClient:
    global _hf_client
    if _hf_client is None:
        _hf_client = HuggingFaceClient()
    return _hf_client
