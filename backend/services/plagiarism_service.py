"""Plagiarism detection: transcript similarity + CLIP visual similarity."""

from __future__ import annotations

import difflib
import hashlib
import logging
from pathlib import Path
from typing import Any

import numpy as np

from core.constants import PLAGIARISM_SIMILARITY_THRESHOLD
from services.pipeline.config import PIPELINE_DRY_RUN

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy-loaded CLIP model (heavy — only loaded once on first real call)
# ---------------------------------------------------------------------------
_clip_model = None
_clip_processor = None


def _load_clip():
    """Load CLIP model and processor on first use (skipped in dry-run)."""
    global _clip_model, _clip_processor
    if _clip_model is not None:
        return

    try:
        import torch  # noqa: F401
        from transformers import CLIPModel, CLIPProcessor

        model_id = "openai/clip-vit-base-patch32"
        logger.info("Loading CLIP model: %s …", model_id)
        _clip_processor = CLIPProcessor.from_pretrained(model_id)
        _clip_model = CLIPModel.from_pretrained(model_id)
        _clip_model.eval()
        logger.info("CLIP model loaded successfully.")
    except Exception as exc:
        logger.warning("Could not load CLIP model (%s). Falling back to mock embeddings.", exc)


def _embed_image_clip(image_path: str) -> np.ndarray:
    """
    Return an L2-normalised 512-d embedding for an image crop.

    In PIPELINE_DRY_RUN mode (or if the model failed to load), we produce a
    deterministic 512-d vector derived from the file's SHA-256 hash.  This
    guarantees that identical files produce identical embeddings and different
    files produce different embeddings — perfect for integration testing.
    """
    path = Path(image_path)

    # ── Dry-run / fallback: deterministic hash-based mock embedding ────────
    if PIPELINE_DRY_RUN or _clip_model is None:
        if not path.exists():
            # If file doesn't exist, use path string as seed
            seed = hashlib.sha256(str(path).encode()).digest()
        else:
            seed = hashlib.sha256(path.read_bytes()).digest()

        # Expand 32-byte hash → 512 floats via a seeded PRNG
        rng = np.random.RandomState(
            int.from_bytes(seed[:4], "big")
        )
        vec = rng.randn(512).astype(np.float32)
        vec /= np.linalg.norm(vec)
        return vec

    # ── Real CLIP inference ───────────────────────────────────────────────
    import torch
    from PIL import Image

    _load_clip()

    image = Image.open(path).convert("RGB")
    inputs = _clip_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        embedding = _clip_model.get_image_features(**inputs)
    vec = embedding[0].cpu().numpy()
    vec = vec / np.linalg.norm(vec)
    return vec


# ---------------------------------------------------------------------------
# 1.  Transcript-based (text) plagiarism  — existing
# ---------------------------------------------------------------------------

def detect_similar_pairs(
    transcripts: dict[str, str],
    threshold: float = PLAGIARISM_SIMILARITY_THRESHOLD,
) -> list[dict[str, Any]]:
    """
    Compare question transcripts pairwise (same exam upload).
    Returns list of flagged pairs.
    """
    ids = list(transcripts.keys())
    flags: list[dict[str, Any]] = []

    for i, a in enumerate(ids):
        text_a = (transcripts[a] or "").strip()
        if len(text_a) < 40:
            continue
        for b in ids[i + 1 :]:
            text_b = (transcripts[b] or "").strip()
            if len(text_b) < 40:
                continue
            ratio = difflib.SequenceMatcher(None, text_a, text_b).ratio()
            if ratio >= threshold:
                flags.append(
                    {
                        "question_a": a,
                        "question_b": b,
                        "similarity": round(ratio, 3),
                        "reason": f"Transcripts {ratio:.0%} similar",
                    }
                )
    return flags


# ---------------------------------------------------------------------------
# 2.  CLIP visual plagiarism  — NEW
# ---------------------------------------------------------------------------

def detect_visual_plagiarism(
    crop_image_paths: dict[str, str],
    threshold: float = PLAGIARISM_SIMILARITY_THRESHOLD,
) -> list[dict[str, Any]]:
    """
    Compare question crop images pairwise using CLIP embeddings.

    Parameters
    ----------
    crop_image_paths : dict[str, str]
        Mapping of identifier (e.g. question_id or student_id) → absolute
        path to the crop PNG/JPG on disk.
    threshold : float
        Cosine similarity threshold above which a pair is flagged.

    Returns
    -------
    list[dict]
        Each entry:  question_a, question_b, similarity, reason, flag
    """
    if not PIPELINE_DRY_RUN and _clip_model is None:
        _load_clip()

    ids = list(crop_image_paths.keys())
    if len(ids) < 2:
        return []

    # Compute embeddings
    embeddings: dict[str, np.ndarray] = {}
    for cid, img_path in crop_image_paths.items():
        try:
            embeddings[cid] = _embed_image_clip(img_path)
        except Exception as exc:
            logger.warning("Skipping visual embedding for %s: %s", cid, exc)

    # Pairwise cosine similarity (vectors are already L2-normalised)
    flags: list[dict[str, Any]] = []
    embed_ids = list(embeddings.keys())
    for i in range(len(embed_ids)):
        for j in range(i + 1, len(embed_ids)):
            cosine_sim = float(
                np.dot(embeddings[embed_ids[i]], embeddings[embed_ids[j]])
            )
            if cosine_sim >= threshold:
                flags.append(
                    {
                        "question_a": embed_ids[i],
                        "question_b": embed_ids[j],
                        "similarity": round(cosine_sim, 3),
                        "reason": f"Visual similarity {cosine_sim:.0%} (CLIP)",
                        "flag": "VISUAL_PLAGIARISM_SUSPECTED",
                    }
                )

    if flags:
        logger.info(
            "CLIP visual plagiarism: %d pair(s) flagged above %.2f threshold.",
            len(flags),
            threshold,
        )
    return flags


# ---------------------------------------------------------------------------
# 3.  Cross-upload plagiarism (different student papers, same rubric batch)
# ---------------------------------------------------------------------------

def _transcripts_for_upload(db, upload_id: int) -> dict[str, str]:
    """Load question_id → OCR transcript for a graded upload from the DB."""
    from models.grading_result import GradingResult
    from models.question_crop import QuestionCrop

    transcripts: dict[str, str] = {}
    for gr in db.query(GradingResult).all():
        meta = gr.coordinator_output or {}
        if int(meta.get("upload_id") or -1) != upload_id:
            continue
        crop = (
            db.query(QuestionCrop)
            .filter(QuestionCrop.id == gr.question_crop_id)
            .first()
        )
        if crop and crop.question_id:
            transcripts[crop.question_id] = (crop.ocr_text or "").strip()
    return transcripts


def detect_cross_upload_plagiarism(
    db,
    *,
    current_upload_id: int,
    owner_id: int | None,
    rubric_path: str | None,
    current_transcripts: dict[str, str],
    threshold: float = PLAGIARISM_SIMILARITY_THRESHOLD,
) -> list[dict[str, Any]]:
    """
    Compare this upload's answers to other exams from the same instructor
    that share the same rubric (bulk class set).
    """
    if not owner_id:
        return []

    from models.upload_model import UploadedFile

    others = (
        db.query(UploadedFile)
        .filter(
            UploadedFile.owner_id == owner_id,
            UploadedFile.id != current_upload_id,
            UploadedFile.rubric_path == rubric_path,
            UploadedFile.status.in_(("graded", "extracted", "processing")),
        )
        .all()
    )
    if not others:
        return []

    flags: list[dict[str, Any]] = []
    for other in others:
        other_texts = _transcripts_for_upload(db, other.id)
        if not other_texts:
            continue
        for qid, text_a in current_transcripts.items():
            text_a = (text_a or "").strip()
            if len(text_a) < 40:
                continue
            text_b = (other_texts.get(qid) or "").strip()
            if len(text_b) < 40:
                continue
            ratio = difflib.SequenceMatcher(None, text_a, text_b).ratio()
            if ratio >= threshold:
                flags.append(
                    {
                        "question_a": qid,
                        "question_b": qid,
                        "upload_a": current_upload_id,
                        "upload_b": other.id,
                        "similarity": round(ratio, 3),
                        "reason": (
                            f"Cross-paper Q{qid}: uploads {current_upload_id} vs "
                            f"{other.id} are {ratio:.0%} similar"
                        ),
                        "flag": "CROSS_PAPER_PLAGIARISM_SUSPECTED",
                    }
                )
    return flags
