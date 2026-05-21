"""LangGraph state machine for the Tribunal grading pipeline."""

from typing import Any, TypedDict

from langgraph.graph import StateGraph, START, END
from services.tribunal_agents import run_grader, run_critic
from pipeline.tribunal.coordinator import resolve_tribunal_decision
from pipeline.verify.escalation_engine import should_escalate_to_human


class TribunalState(TypedDict):
    tribunal_ctx: dict[str, Any]
    grader_output: dict[str, Any]
    critic_output: dict[str, Any]
    resolution: dict[str, Any]
    escalate: bool
    escalation_reasons: list[str]


def grader_node(state: TribunalState) -> dict:
    """Runs the grader agent."""
    # In a real retry loop, we might inject critic feedback into tribunal_ctx here
    grader_output = run_grader(state["tribunal_ctx"])
    return {"grader_output": grader_output}


def critic_node(state: TribunalState) -> dict:
    """Runs the critic agent."""
    critic_output = run_critic(state["tribunal_ctx"], state["grader_output"])
    return {"critic_output": critic_output}


def resolution_node(state: TribunalState) -> dict:
    """Resolves final decision and determines escalation."""
    resolution = resolve_tribunal_decision(state["grader_output"], state["critic_output"])
    escalate, escalation_reasons = should_escalate_to_human(
        state["tribunal_ctx"], state["grader_output"], state["critic_output"]
    )
    return {
        "resolution": resolution,
        "escalate": escalate,
        "escalation_reasons": escalation_reasons
    }


# Build the graph
workflow = StateGraph(TribunalState)

workflow.add_node("grader", grader_node)
workflow.add_node("critic", critic_node)
workflow.add_node("resolution", resolution_node)

workflow.add_edge(START, "grader")
workflow.add_edge("grader", "critic")
workflow.add_edge("critic", "resolution")
workflow.add_edge("resolution", END)

app = workflow.compile()
