"""Run the full EXTRACT phase for one upload."""

from __future__ import annotations

import json
from pathlib import Path

from services.pipeline.extract.context_assembler import assemble_all
from services.pipeline.extract.ocr import extract_transcript, should_bypass_ocr
from services.pipeline.schemas import ExtractPhaseResult, GradingRubric
from services.vision.vision_router import (
    _resolve_upload_path,
    page_to_question_crops,
    pdf_to_page_images,
)


def load_rubric(rubric_path: str | Path | None) -> GradingRubric:
    if rubric_path and Path(rubric_path).exists():
        data = json.loads(Path(rubric_path).read_text())
        return GradingRubric.model_validate(data)
    return GradingRubric(
        exam_id="default",
        course="",
        questions=[
            {
                "id": "q1",
                "title": "Question 1",
                "max_points": 10.0,
                "criteria": [
                    {
                        "id": "c1",
                        "description": "Correctness and clarity",
                        "max_points": 10.0,
                    }
                ],
            }
        ],
    )


def run_extract_phase(
    upload_id: int,
    file_path: str,
    rubric_path: str | None = None,
    rubric_json: dict | None = None,
) -> ExtractPhaseResult:
    path = _resolve_upload_path(file_path)
    if not path.exists():
        raise FileNotFoundError(file_path)

    rubric = (
        GradingRubric.model_validate(rubric_json)
        if rubric_json
        else load_rubric(rubric_path)
    )

    out_dir = Path("uploads/processed") / str(upload_id)
    out_dir.mkdir(parents=True, exist_ok=True)

    suffix = path.suffix.lower()
    if suffix in {".png", ".jpg", ".jpeg"}:
        from services.pipeline.schemas import PageCrop

        pages = [
            PageCrop(page_index=0, image_path=str(path)),
        ]
    else:
        pages = pdf_to_page_images(path, out_dir)

    question_ids = [q.id for q in rubric.questions]
    crops = []
    for page in pages:
        crops.extend(page_to_question_crops(page, question_ids))

    ocrs = {}
    for crop in crops:
        ocr = extract_transcript(crop)
        if should_bypass_ocr(crop, ocr):
            crop.bypass_ocr = True
        ocrs[crop.question_id] = ocr

    contexts = assemble_all(upload_id, crops, ocrs, rubric)

    return ExtractPhaseResult(
        upload_id=upload_id,
        pages=pages,
        questions=crops,
        contexts=contexts,
        status="extracted",
    )
