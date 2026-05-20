from db.session import SessionLocal

from models.question_crop import QuestionCrop
from pipeline.extraction.ocr_pipeline import (
    run_ocr_pipeline
)


db = SessionLocal()

crop = (
    db.query(QuestionCrop)
    .first()
)

updated_crop = run_ocr_pipeline(
    db=db,
    crop=crop
)

print(updated_crop.ocr_text)
print(updated_crop.status)