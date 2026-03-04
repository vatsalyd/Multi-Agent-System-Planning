"""
Retrieval Agent — optimizes search queries and retrieves docs from ChromaDB.
"""

import logging

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from app.config import settings
from app.rag.vectorstore import similarity_search

logger = logging.getLogger(__name__)

RETRIEVAL_SYSTEM_PROMPT = """You are a search query optimization specialist. Given a support ticket and its classified category, your job is to generate an optimized search query that will retrieve the most relevant company policy documents.

Rules:
- Extract the core question or problem from the ticket
- Include relevant keywords related to the category
- Remove filler words and irrelevant details
- The query should be 10-20 words maximum
- Respond with ONLY the optimized search query, nothing else"""


def create_retrieval_agent() -> ChatGroq:
    return ChatGroq(
        model=settings.groq_model,
        groq_api_key=settings.groq_api_key,
        temperature=0.0,
    )


def retrieve_documents(ticket_text: str, category: str, k: int = 5) -> list:
    """Optimize the search query via LLM, then retrieve relevant docs from ChromaDB."""
    logger.info(f"Retrieving documents for category: {category}")

    llm = create_retrieval_agent()
    messages = [
        SystemMessage(content=RETRIEVAL_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Category: {category}\n"
                f"Ticket: {ticket_text}\n\n"
                f"Generate an optimized search query:"
            )
        ),
    ]
    response = llm.invoke(messages)
    optimized_query = response.content.strip()
    logger.info(f"Optimized search query: {optimized_query}")

    docs = similarity_search(optimized_query, k=k)

    results = []
    for doc in docs:
        results.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
        })

    logger.info(f"Retrieved {len(results)} document chunks")
    return results
