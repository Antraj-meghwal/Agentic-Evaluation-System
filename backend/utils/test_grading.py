from db.session import SessionLocal

from models.question_crop import QuestionCrop
from pipeline.tribunal.context_assembler import (
    build_grading_context
)
from pipeline.tribunal.grading_pipeline import (
    run_grading_pipeline
)
from services.rubric_service import load_rubric


db = SessionLocal()

rubric = load_rubric(
    "data/rubrics/sample_rubric.json"
)

crop = db.query(QuestionCrop).first()

if crop is None:

    print("No QuestionCrop found")

    exit()
    
submission = crop.submission

context = build_grading_context(
    crop=crop,
    submission=submission,
    rubric=rubric
)

grading_result = run_grading_pipeline(
    db=db,
    crop=crop,
    grading_context=context
)

print(grading_result.final_score)
print(grading_result.grader_output)