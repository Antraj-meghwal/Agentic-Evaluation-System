from sqlalchemy.orm import Session

from models.grading_result import (
    GradingResult,
)
from models.question_crop import (
    CropStatus,
    QuestionCrop
)

from pipeline.tribunal.hf_grader import (
    HuggingFaceVLMGrader
)

from pipeline.tribunal.critic_agent import (
    CriticAgent
)

from pipeline.tribunal.coordinator import (
    resolve_tribunal_decision
)

from pipeline.tribunal.rag_store import (
    RAGVectorStore
)

from pipeline.verify.escalation_engine import (
    should_escalate_to_human
)


def run_grading_pipeline(
    db: Session,
    crop: QuestionCrop,
    grading_context: dict
):
    """
    Execute complete tribunal grading pipeline.
    """

    # -----------------------------------
    # Primary Vision-Language Grader
    # -----------------------------------

    grader = HuggingFaceVLMGrader()

    grader_output = grader.grade(
        grading_context
    )

    # -----------------------------------
    # Critic Review
    # -----------------------------------

    critic = CriticAgent()

    critic_output = critic.review(
        grading_context=grading_context,
        grader_output=grader_output
    )

    # -----------------------------------
    # Tribunal Resolution
    # -----------------------------------

    resolution = resolve_tribunal_decision(
        grader_output=grader_output,
        critic_output=critic_output
    )

    # -----------------------------------
    # Governance Escalation
    # -----------------------------------

    escalate, escalation_reasons = (
        should_escalate_to_human(
            grading_context=grading_context,
            grader_output=grader_output,
            critic_output=critic_output
        )
    )

    # -----------------------------------
    # Persist Tribunal Result
    # -----------------------------------

    grading_result = GradingResult(
        question_crop_id=crop.id,

        final_score=resolution[
            "final_score"
        ],

        max_score=grader_output[
            "max_score"
        ],

        confidence_score=grader_output[
            "confidence"
        ],

        resolution_status=resolution[
            "resolution_status"
        ],

        requires_human_review=(
            resolution["requires_human_review"]
            or escalate
        ),

        grader_output=grader_output,

        critic_output=critic_output,

        coordinator_output={
            "escalation_reasons":
            escalation_reasons
        },

        final_feedback=grader_output[
            "feedback"
        ]
    )

    db.add(grading_result)

    # -----------------------------------
    # Update Crop Lifecycle
    # -----------------------------------

    crop.status = CropStatus.GRADED

    db.commit()

    db.refresh(grading_result)

    # -----------------------------------
    # Store Semantic Memory (RAG)
    # -----------------------------------

    rag_store = RAGVectorStore()

    rag_store.add_answer(
        crop_id=str(crop.id),

        question_id=crop.question_id,

        answer_text=crop.ocr_text or "",

        final_score=grading_result.final_score
    )

    return grading_result