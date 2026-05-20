from models.grading_result import (
    ResolutionStatus
)


def analyze_tribunal_result(
    grading_result
):
    """
    Analyze tribunal agreement patterns.
    """

    analysis = {

        "critic_disagreed":
        (
            grading_result
            .resolution_status
            !=
            ResolutionStatus
            .GRADER_ACCEPTED
        ),

        "required_human":
        grading_result
        .requires_human_review,

        "confidence":
        grading_result
        .confidence_score
    }

    return analysis