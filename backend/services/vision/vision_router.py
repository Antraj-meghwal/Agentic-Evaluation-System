"""PDF ingestion: split pages and produce question-level crops."""

from __future__ import annotations

import os
from pathlib import Path

from pdf2image import convert_from_path
from PIL import Image

from services.pipeline.config import PROCESSED_DIR, UPLOADS_DIR
from services.pipeline.schemas import PageCrop, QuestionCrop


def _resolve_upload_path(relative_or_absolute: str) -> Path:
    path = Path(relative_or_absolute)
    if path.is_absolute() and path.exists():
        return path
    cleaned = relative_or_absolute.lstrip("/")
    for prefix in ("uploads/", UPLOADS_DIR + "/"):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix) :]
    candidate = Path(UPLOADS_DIR) / cleaned
    if candidate.exists():
        return candidate
    return Path(relative_or_absolute)


def pdf_to_page_images(pdf_path: str | Path, output_dir: Path) -> list[PageCrop]:
    """Convert each PDF page to a PNG in output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = convert_from_path(str(pdf_path), dpi=200)
    crops: list[PageCrop] = []
    for idx, page in enumerate(pages):
        out = output_dir / f"page_{idx:03d}.png"
        page.save(out, "PNG")
        w, h = page.size
        crops.append(
            PageCrop(
                page_index=idx,
                image_path=str(out),
                width=w,
                height=h,
            )
        )
    return crops


def page_to_question_crops(
    page: PageCrop,
    question_ids: list[str] | None = None,
) -> list[QuestionCrop]:
    """
    Simple splitter: one question crop per page for now.
    Step 2+ can add layout detection / instructor-defined regions.
    """
    qids = question_ids or [f"q{page.page_index + 1}"]
    if len(qids) == 1:
        return [
            QuestionCrop(
                question_id=qids[0],
                page_index=page.page_index,
                image_path=page.image_path,
                bypass_ocr=False,
            )
        ]
    img = Image.open(page.image_path)
    w, h = img.size
    n = len(qids)
    band_h = h // n
    results: list[QuestionCrop] = []
    base = Path(page.image_path).parent
    for i, qid in enumerate(qids):
        top = i * band_h
        bottom = h if i == n - 1 else (i + 1) * band_h
        crop = img.crop((0, top, w, bottom))
        out = base / f"{qid}_p{page.page_index:03d}.png"
        crop.save(out, "PNG")
        results.append(
            QuestionCrop(
                question_id=qid,
                page_index=page.page_index,
                image_path=str(out),
                bypass_ocr=False,
            )
        )
    return results


def prepare_document_for_grading(
    file_path: str,
    upload_id: int | None = None,
    question_ids: list[str] | None = None,
) -> list[str]:
    """
    Legacy API used by grading_routes: returns list of image paths.
    """
    path = _resolve_upload_path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Upload not found: {file_path}")

    suffix = path.suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg"}:
        return [str(path)]

    uid = upload_id if upload_id is not None else path.stem
    out_dir = Path(PROCESSED_DIR) / str(uid)
    pages = pdf_to_page_images(path, out_dir)
    all_crops: list[QuestionCrop] = []
    for page in pages:
        all_crops.extend(page_to_question_crops(page, question_ids))
    return [c.image_path for c in all_crops]
