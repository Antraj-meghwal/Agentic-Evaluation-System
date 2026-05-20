import json
from pathlib import Path

from pydantic import ValidationError

from schemas.rubric_schema import RubricSchema


class RubricValidationException(Exception):
    pass


def load_rubric(rubric_path: str) -> RubricSchema:
    """
    Load and validate rubric JSON file.
    """

    path = Path(rubric_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Rubric file not found: {rubric_path}"
        )

    try:
        with open(path, "r") as file:
            rubric_data = json.load(file)

    except json.JSONDecodeError as e:
        raise RubricValidationException(
            f"Invalid JSON format: {str(e)}"
        )

    try:
        validated_rubric = RubricSchema(
            **rubric_data
        )

    except ValidationError as e:
        raise RubricValidationException(
            f"Rubric validation failed:\n{str(e)}"
        )

    return validated_rubric