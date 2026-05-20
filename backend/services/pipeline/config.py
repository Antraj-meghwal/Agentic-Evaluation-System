"""GradeOps Tribunal — Hugging Face model configuration."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class PipelineModels:
    """HF model IDs aligned with gradeops_tribunal_architecture.svg."""

    # EXTRACT: handwriting + formulas
    ocr_vlm: str = "Qwen/Qwen2-VL-7B-Instruct"
    ocr_fallback: str = "facebook/nougat-base"

    # TRIBUNAL (wired in Step 2)
    grader_vlm: str = "Qwen/Qwen2-VL-7B-Instruct"
    critic_llm: str = "meta-llama/Meta-Llama-3-8B-Instruct"
    coordinator_llm: str = "mistralai/Mistral-7B-Instruct-v0.3"

    # VERIFY: embeddings (Step 3)
    embedding: str = "sentence-transformers/all-MiniLM-L6-v2"
    clip: str = "openai/clip-vit-base-patch32"


MODELS = PipelineModels()

HF_TOKEN = os.getenv("HF_TOKEN", "")
HF_API_URL = os.getenv(
    "HF_INFERENCE_URL",
    "https://api-inference.huggingface.co",
)

# Use local/mock when no token (dev without HF billing)
PIPELINE_DRY_RUN = os.getenv("PIPELINE_DRY_RUN", "false").lower() in (
    "1",
    "true",
    "yes",
)

CONSENSUS_SCORE_DELTA = float(os.getenv("CONSENSUS_SCORE_DELTA", "1.0"))
MAX_TRIBUNAL_ROUNDS = int(os.getenv("MAX_TRIBUNAL_ROUNDS", "2"))

UPLOADS_DIR = os.getenv("UPLOADS_DIR", "uploads")
PROCESSED_DIR = os.getenv("PROCESSED_DIR", "uploads/processed")
