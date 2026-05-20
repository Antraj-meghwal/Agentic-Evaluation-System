from db.session import SessionLocal

from models.submission import Submission
from pipeline.ingestion.crop_pipeline import (
    process_submission_crops
)
from services.rubric_service import load_rubric


db = SessionLocal()

rubric = load_rubric(
    "data/rubrics/sample_rubric.json"
)

submission = Submission(
    batch_id="00000000-0000-0000-0000-000000000000",
    student_id="S001",
    original_pdf_path="uploads/EvenSemProjects.pdf"
)

db.add(submission)

db.commit()

db.refresh(submission)

crops = process_submission_crops(
    db=db,
    submission=submission,
    rubric=rubric
)

print(f"Generated {len(crops)} crops.")