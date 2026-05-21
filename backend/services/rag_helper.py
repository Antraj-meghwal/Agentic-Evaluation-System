"""Lightweight RAG helpers for tribunal grading (retrieve + store)."""

from __future__ import annotations

import logging

from core.constants import RAG_TOP_K
from services.pipeline.config import PIPELINE_DRY_RUN

logger = logging.getLogger(__name__)


def retrieve_similar_answers(question_id: str, ocr_text: str) -> list[dict]:
    """Return prior graded answers for consistency (empty in dry-run or on failure)."""
    if PIPELINE_DRY_RUN or not (ocr_text or "").strip():
        return []

    try:
        from pipeline.tribunal.rag_store import RAGVectorStore

        store = RAGVectorStore()
        return store.retrieve_similar_answers(
            question_id=question_id,
            query_text=ocr_text,
            top_k=RAG_TOP_K,
        )
    except Exception as exc:
        logger.warning("RAG retrieval skipped: %s", exc)
        return []


def store_graded_answer(
    *,
    crop_id: str,
    question_id: str,
    answer_text: str,
    final_score: int,
) -> None:
    """Persist a graded answer into the vector store for future retrieval."""
    if PIPELINE_DRY_RUN or not (answer_text or "").strip():
        return

    try:
        from pipeline.tribunal.rag_store import RAGVectorStore

        store = RAGVectorStore()
        store.add_answer(
            crop_id=crop_id,
            question_id=question_id,
            answer_text=answer_text,
            final_score=final_score,
        )
    except Exception as exc:
        logger.warning("RAG store skipped: %s", exc)
