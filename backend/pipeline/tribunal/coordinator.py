from models.grading_result import (
    ResolutionStatus
)


def resolve_tribunal_decision(
    grader_output: dict,
    critic_output: dict
):
    """
    Resolve final grading decision
    between grader and critic.
    """

    if critic_output["approved"]:

        return {
            "final_score":
            grader_output["score"],

            "resolution_status":
            ResolutionStatus.GRADER_ACCEPTED,

            "requires_human_review":
            False
        }

    if critic_output[
        "requires_human_review"
    ]:

        return {
            "final_score":
            critic_output["corrected_score"],

            "resolution_status":
            ResolutionStatus.REQUIRES_HUMAN,

            "requires_human_review":
            True
        }

    return {
        "final_score":
        critic_output["corrected_score"],

        "resolution_status":
        ResolutionStatus.CRITIC_CORRECTED,

        "requires_human_review":
        False
    }