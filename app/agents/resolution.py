"""
Resolution Agent — the "drafter" of the system.

This is the final agent in the pipeline. It receives:
- The original ticket text
- The classified category
- The retrieved document chunks from the knowledge base

It then generates a professional, empathetic resolution draft that
directly addresses the employee's issue using information from the
company documentation, with inline citations.

Why citations?
- Builds trust — the employee can verify the answer
- Prevents hallucination — forces the agent to ground responses in docs
- Audit trail — for compliance and quality assurance
"""

import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.config import settings

logger = logging.getLogger(__name__)

RESOLUTION_SYSTEM_PROMPT = """You are a professional corporate support resolution specialist. You write clear, helpful, and empathetic response drafts for employee support tickets.

You will receive:
1. The original ticket from an employee
2. The classified category
3. Relevant excerpts from company policy documents

Your job is to write a resolution draft that:
- Directly addresses the employee's specific issue
- Uses information from the provided documents
- Includes inline citations in the format [Source: filename.md]
- Is professional, empathetic, and actionable
- Provides step-by-step instructions when applicable
- Mentions relevant contact information or escalation paths if appropriate

Format your response as:
RESOLUTION:
<your resolution text>

SOURCES:
<list of source documents used>

Keep the resolution concise but thorough (150-300 words)."""


def create_resolution_agent() -> ChatOpenAI:
    """Create the LLM instance for the Resolution Agent."""
    return ChatOpenAI(
        model=settings.openai_model,
        openai_api_key=settings.openai_api_key,
        temperature=0.3,  # Slight creativity for natural language
    )


def generate_resolution(
    ticket_text: str,
    category: str,
    retrieved_docs: list,
) -> dict:
    """
    Generate a resolution draft for a classified ticket.

    Args:
        ticket_text: The original ticket text.
        category: The classified category.
        retrieved_docs: List of dicts with 'content' and 'source' keys.

    Returns:
        dict with 'resolution' and 'sources' keys.
    """
    logger.info(f"Generating resolution for category: {category}")

    # Format the retrieved documents for the prompt
    docs_text = ""
    sources = set()
    for i, doc in enumerate(retrieved_docs, 1):
        docs_text += f"\n--- Document {i} (Source: {doc['source']}) ---\n"
        docs_text += doc["content"]
        docs_text += "\n"
        sources.add(doc["source"])

    llm = create_resolution_agent()

    messages = [
        SystemMessage(content=RESOLUTION_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"CATEGORY: {category}\n\n"
                f"ORIGINAL TICKET:\n{ticket_text}\n\n"
                f"RELEVANT COMPANY DOCUMENTS:\n{docs_text}\n\n"
                f"Please write a resolution draft."
            )
        ),
    ]

    response = llm.invoke(messages)
    resolution_text = response.content.strip()

    logger.info("Resolution generated successfully")

    return {
        "resolution": resolution_text,
        "sources": list(sources),
    }
