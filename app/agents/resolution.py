"""
Resolution Agent — generates citation-backed response drafts using Groq.
"""

from langchain_core.messages import SystemMessage, HumanMessage

from app.llm.provider import create_llm
from app.logging_config import get_logger

logger = get_logger(__name__)

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


async def generate_resolution(
    ticket_text: str,
    category: str,
    retrieved_docs: list,
) -> dict:
    """Generate a resolution draft using the ticket, category, and retrieved documents."""
    logger.info("Generating resolution for category: %s", category)

    docs_text = ""
    sources = set()
    for i, doc in enumerate(retrieved_docs, 1):
        docs_text += f"\n--- Document {i} (Source: {doc.source}) ---\n"
        docs_text += doc.content
        docs_text += "\n"
        sources.add(doc.source)

    llm = create_llm(temperature=0.3)

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

    response = await llm.ainvoke(messages)
    resolution_text = response.content.strip()

    logger.info("Resolution generated successfully")

    return {
        "resolution": resolution_text,
        "sources": list(sources),
    }