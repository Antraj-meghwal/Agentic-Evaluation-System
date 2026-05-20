"""Lightweight transcript similarity check within one upload batch."""

from __future__ import annotations

import difflib
from typing import Any

from core.constants import PLAGIARISM_SIMILARITY_THRESHOLD


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
