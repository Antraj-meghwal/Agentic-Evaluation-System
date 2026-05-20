from models.grading_result import (
    ResolutionStatus
)


def compute_grading_metrics(
    grading_result
):
    """
    Compute grading analytics metrics.
    """

    metrics = {

        "final_score":
        grading_result.final_score,

        "confidence":
        grading_result.confidence_score,

        "requires_human_review":
        grading_result.requires_human_review,

        "resolution_status":
        grading_result.resolution_status.value
    }

    return metrics