"""
LangGraph Orchestration Graph — the "brain" of the system.

This module defines the state machine that connects all three agents
into a coherent pipeline using LangGraph's StateGraph.

Flow:
    Incoming Ticket → Triage Agent → [Confidence Check]
        ├── High confidence → Retrieval Agent → Resolution Agent → Response
        └── Low confidence  → Human Escalation → Response

Why LangGraph?
- Explicit, debuggable state management between agents
- Conditional routing (e.g., escalation on low confidence)
- Built-in support for retries, breakpoints, and streaming
- Production-ready orchestration (used by LangChain team)

State Schema:
    The state is a TypedDict that flows through all nodes. Each agent
    reads from and writes to specific fields, creating a clean data
    pipeline without tight coupling between agents.
"""

import logging
import time
import uuid
from typing import TypedDict

from langgraph.graph import StateGraph, END

from app.agents.triage import triage_ticket
from app.agents.retrieval import retrieve_documents
from app.agents.resolution import generate_resolution

logger = logging.getLogger(__name__)

# ── Confidence threshold for routing ────────────────────────
# If the Triage Agent's confidence is below this, the ticket
# is routed to human escalation instead of automated resolution.
CONFIDENCE_THRESHOLD = 0.5


# ── State Schema ────────────────────────────────────────────
class AgentState(TypedDict):
    """
    The shared state that flows through the agent pipeline.

    Each node reads from and writes to this state.
    """
    # Input
    ticket_id: str
    ticket_text: str
    source: str

    # Triage Agent output
    category: str
    confidence: float
    summary: str

    # Retrieval Agent output
    retrieved_docs: list

    # Resolution Agent output
    resolution: str
    sources: list

    # Pipeline metadata
    status: str
    processing_time_ms: float
    error: str


# ── Node Functions ──────────────────────────────────────────
# Each function takes the full state and returns a partial update.

def triage_node(state: AgentState) -> dict:
    """
    Node 1: Classify the incoming ticket.

    Reads: ticket_text
    Writes: category, confidence, summary
    """
    logger.info(f"[Triage Node] Processing ticket {state['ticket_id']}")

    try:
        result = triage_ticket(state["ticket_text"])
        return {
            "category": result["category"],
            "confidence": result["confidence"],
            "summary": result["summary"],
            "status": "triaged",
        }
    except Exception as e:
        logger.error(f"[Triage Node] Error: {e}")
        return {
            "category": "GENERAL",
            "confidence": 0.0,
            "summary": "Triage failed",
            "status": "error",
            "error": str(e),
        }


def retrieval_node(state: AgentState) -> dict:
    """
    Node 2: Retrieve relevant documents.

    Reads: ticket_text, category
    Writes: retrieved_docs
    """
    logger.info(
        f"[Retrieval Node] Searching docs for "
        f"category: {state['category']}"
    )

    try:
        docs = retrieve_documents(
            ticket_text=state["ticket_text"],
            category=state["category"],
            k=5,
        )
        return {
            "retrieved_docs": docs,
            "status": "documents_retrieved",
        }
    except Exception as e:
        logger.error(f"[Retrieval Node] Error: {e}")
        return {
            "retrieved_docs": [],
            "status": "retrieval_error",
            "error": str(e),
        }


def resolution_node(state: AgentState) -> dict:
    """
    Node 3: Generate a resolution draft.

    Reads: ticket_text, category, retrieved_docs
    Writes: resolution, sources
    """
    logger.info("[Resolution Node] Generating resolution draft")

    try:
        result = generate_resolution(
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
        logger.error(f"[Resolution Node] Error: {e}")
        return {
            "resolution": f"Unable to generate resolution: {e}",
            "sources": [],
            "status": "resolution_error",
            "error": str(e),
        }


def escalation_node(state: AgentState) -> dict:
    """
    Fallback node: Route to human when confidence is too low.

    This fires when the Triage Agent isn't confident enough to
    classify the ticket correctly.
    """
    logger.info(
        f"[Escalation Node] Low confidence ({state['confidence']}), "
        f"escalating to human"
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


# ── Routing Logic ───────────────────────────────────────────

def should_escalate(state: AgentState) -> str:
    """
    Conditional edge: determine if the ticket should be escalated.

    Returns:
        "retrieve" if confidence is above threshold
        "escalate" if confidence is below threshold
    """
    if state.get("confidence", 0) < CONFIDENCE_THRESHOLD:
        logger.info(
            f"Confidence {state.get('confidence', 0)} < "
            f"{CONFIDENCE_THRESHOLD}, routing to escalation"
        )
        return "escalate"
    return "retrieve"


# ── Graph Construction ──────────────────────────────────────

def build_graph() -> StateGraph:
    """
    Construct the LangGraph state machine.

    Graph structure:
        triage → [check confidence] → retrieval → resolution → END
                                    ↘ escalation → END
    """
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("triage", triage_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("resolution", resolution_node)
    graph.add_node("escalation", escalation_node)

    # Set the entry point
    graph.set_entry_point("triage")

    # Conditional edge: triage → retrieval OR escalation
    graph.add_conditional_edges(
        "triage",
        should_escalate,
        {
            "retrieve": "retrieval",
            "escalate": "escalation",
        },
    )

    # Linear edges
    graph.add_edge("retrieval", "resolution")
    graph.add_edge("resolution", END)
    graph.add_edge("escalation", END)

    return graph.compile()


# ── Public API ──────────────────────────────────────────────

# Compile the graph once at module load time
compiled_graph = build_graph()


def process_ticket(ticket_text: str, source: str = "api") -> dict:
    """
    Process a ticket through the full agent pipeline.

    This is the main entry point for the orchestration system.

    Args:
        ticket_text: The raw text of the incoming support ticket.
        source: Where the ticket came from (e.g., "webhook", "api").

    Returns:
        The final state dict with all agent outputs.
    """
    start_time = time.time()

    # Initialize the state
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

    logger.info(
        f"Processing ticket {initial_state['ticket_id']} "
        f"from {source}"
    )

    # Run the graph
    final_state = compiled_graph.invoke(initial_state)

    # Calculate processing time
    elapsed = (time.time() - start_time) * 1000
    final_state["processing_time_ms"] = round(elapsed, 2)

    logger.info(
        f"Ticket {final_state['ticket_id']} processed in "
        f"{final_state['processing_time_ms']}ms — "
        f"status: {final_state['status']}"
    )

    return final_state
