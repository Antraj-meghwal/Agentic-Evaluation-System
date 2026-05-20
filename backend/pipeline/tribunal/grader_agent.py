import random


def run_grader_agent(
    grading_context: dict
):
    """
    Mock grading agent.

    Later replaced with:
    Gemini Vision / GPT-4o.
    """

    rubric = grading_context["rubric"]

    max_points = rubric["max_points"]

    awarded_score = random.randint(
        max_points // 2,
        max_points
    )

    confidence = round(
        random.uniform(0.7, 0.98),
        2
    )

    feedback = (
        "Student demonstrates reasonable "
        "understanding of the concept."
    )

    criteria_breakdown = []

    for criterion in rubric["criteria"]:

        earned = min(
            criterion["points"],
            random.randint(
                0,
                criterion["points"]
            )
        )

        criteria_breakdown.append(
            {
                "criterion_id": criterion["id"],
                "awarded_points": earned,
                "max_points": criterion["points"],
                "reasoning": (
                    "Criterion partially satisfied."
                )
            }
        )

    result = {
        "score": awarded_score,
        "max_score": max_points,
        "confidence": confidence,
        "feedback": feedback,
        "criteria_breakdown": (
            criteria_breakdown
        )
    }

    return result