"""
LangGraph orchestration — connects Triage, Retrieval, and Resolution agents
into a state machine with conditional routing.
"""

import time
import uuid
from typing import TypedDict

from langgraph.graph import StateGraph, END

from app.agents.triage import triage_ticket
from app.agents.retrieval import retrieve_documents
from app.agents.resolution import generate_resolution
from app.logging_config import get_logger

logger = get_logger(__name__)

CONFIDENCE_THRESHOLD = 0.5


class AgentState(TypedDict):
    """Shared state that flows through the agent pipeline."""
    ticket_id: str
    ticket_text: str
    source: str
    category: str
    confidence: float
    summary: str
    retrieved_docs: list
    resolution: str
    sources: list
    status: str
    processing_time_ms: float
    error: str


async def triage_node(state: AgentState) -> dict:
    logger.info("[Triage Node] Processing ticket %s", state["ticket_id"])
    try:
        result = await triage_ticket(state["ticket_text"])
        return {
            "category": result["category"],
            "confidence": result["confidence"],
            "summary": result["summary"],
            "status": "triaged",
        }
    except Exception as e:
        logger.error("[Triage Node] Error: %s", e)
        return {
            "category": "GENERAL",
            "confidence": 0.0,
            "summary": "Triage failed",
            "status": "error",
            "error": str(e),
        }


async def retrieval_node(state: AgentState) -> dict:
    logger.info("[Retrieval Node] Searching docs for category: %s", state["category"])
    try:
        docs = await retrieve_documents(
            ticket_text=state["ticket_text"],
            category=state["category"],
            k=5,
        )
        return {
            "retrieved_docs": docs,
            "status": "documents_retrieved",
        }
    except Exception as e:
        logger.error("[Retrieval Node] Error: %s", e)
        return {
            "retrieved_docs": [],
            "status": "retrieval_error",
            "error": str(e),
        }


async def resolution_node(state: AgentState) -> dict:
    logger.info("[Resolution Node] Generating resolution draft")
    try:
        result = await generate_resolution(
            ticket_text=state["ticket_text"],
            category=state["category"],
            retrieved_docs=state["retrieved_docs"],
        )
        return {
            "resolution": result["resolution"],
            "sources": result["sources"],
            "status": "resolved",
        }
    except Exception as e:
        logger.error("[Resolution Node] Error: %s", e)
        return {
            "resolution": f"Unable to generate resolution: {e}",
            "sources": [],
            "status": "resolution_error",
            "error": str(e),
        }


def escalation_node(state: AgentState) -> dict:
    logger.info(
        "[Escalation Node] Low confidence (%s), escalating", state["confidence"]
    )
    return {
        "resolution": (
            "This ticket requires human review. The automated triage system "
            f"was unable to confidently classify this request "
            f"(confidence: {state['confidence']:.2f}). "
            "The ticket has been escalated to a human agent for review."
        ),
        "sources": [],
        "status": "escalated",
    }


def should_escalate(state: AgentState) -> str:
    if state.get("confidence", 0) < CONFIDENCE_THRESHOLD:
        return "escalate"
    return "retrieve"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("node_triage", triage_node)
    graph.add_node("node_retrieval", retrieval_node)
    graph.add_node("node_resolution", resolution_node)
    graph.add_node("node_escalation", escalation_node)

    graph.set_entry_point("node_triage")

    # Conditional routing: high confidence -> retrieve, low -> escalate
    graph.add_conditional_edges(
        "node_triage",
        should_escalate,
        {
            "retrieve": "node_retrieval",
            "escalate": "node_escalation",
        },
    )

    graph.add_edge("node_retrieval", "node_resolution")
    graph.add_edge("node_resolution", END)
    graph.add_edge("node_escalation", END)

    return graph.compile()


# Compile once at module load
compiled_graph = build_graph()


async def process_ticket(ticket_text: str, source: str = "api") -> dict:
    """Process a ticket through the full agent pipeline."""
    start_time = time.time()

    initial_state: AgentState = {
        "ticket_id": str(uuid.uuid4()),
        "ticket_text": ticket_text,
        "source": source,
        "category": "",
        "confidence": 0.0,
        "summary": "",
        "retrieved_docs": [],
        "resolution": "",
        "sources": [],
        "status": "pending",
        "processing_time_ms": 0.0,
        "error": "",
    }

    logger.info("Processing ticket %s from %s", initial_state["ticket_id"], source)

    final_state = await compiled_graph.ainvoke(initial_state)

    elapsed = (time.time() - start_time) * 1000
    final_state["processing_time_ms"] = round(elapsed, 2)

    logger.info(
        "Ticket %s processed in %sms — status: %s",
        final_state["ticket_id"],
        final_state["processing_time_ms"],
        final_state["status"],
    )

    return final_state