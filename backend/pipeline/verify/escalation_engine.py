from models.grading_result import (
    ResolutionStatus
)


def should_escalate_to_human(
    grading_context: dict,
    grader_output: dict,
    critic_output: dict
):
    """
    Determine if a grading result should
    be escalated to human review.

    Returns (bool, list[str]) — whether to
    escalate, and the reasons why.
    """

    reasons = []

    # Low confidence from grader
    confidence = grader_output.get(
        "confidence", 1.0
    )

    if confidence < 0.6:

        reasons.append(
            f"Low grader confidence: "
            f"{confidence:.2f}"
        )

    # Large score disagreement between
    # grader and critic
    grader_score = grader_output.get(
        "score", 0
    )

    critic_score = critic_output.get(
        "corrected_score", grader_score
    )

    max_score = grader_output.get(
        "max_score", 1
    )

    if max_score > 0:

        disagreement = (
            abs(grader_score - critic_score)
            / max_score
        )

        if disagreement > 0.3:

            reasons.append(
                f"Score disagreement: "
                f"grader={grader_score}, "
                f"critic={critic_score} "
                f"({disagreement:.0%} of max)"
            )

    # Critic explicitly requests
    # human review
    if critic_output.get(
        "requires_human_review", False
    ):

        reasons.append(
            "Critic flagged for "
            "human review"
        )

    # Critic did not approve and
    # severity is major
    if (
        not critic_output.get(
            "approved", True
        )
        and critic_output.get(
            "severity"
        ) == "major"
    ):

        reasons.append(
            "Critic raised major objections"
        )

    escalate = len(reasons) > 0

    return escalate, reasons


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