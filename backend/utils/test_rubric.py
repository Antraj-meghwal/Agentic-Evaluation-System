from services.rubric_service import load_rubric


rubric = load_rubric(
    "data/rubrics/sample_rubric.json"
)

print(rubric.model_dump())