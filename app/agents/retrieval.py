"""
Retrieval Agent — the "researcher" of the system.

After the Triage Agent classifies a ticket, the Retrieval Agent takes
over. It constructs an optimized search query based on the ticket text
and category, then performs a semantic similarity search against the
ChromaDB vector store to find the most relevant company documentation.

Why a separate Retrieval Agent (instead of just raw vector search)?
- The agent rewrites the query to be more search-friendly
- It can add category-specific context to improve retrieval precision
- It returns structured results with source metadata for citation
"""

import logging

from langchain_openai import ChatOpenAI
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


def create_retrieval_agent() -> ChatOpenAI:
    """Create the LLM instance for the Retrieval Agent."""
    return ChatOpenAI(
        model=settings.openai_model,
        openai_api_key=settings.openai_api_key,
        temperature=0.0,
    )


def retrieve_documents(ticket_text: str, category: str, k: int = 5) -> list:
    """
    Retrieve relevant documents for a classified ticket.

    Steps:
    1. Use LLM to optimize the search query
    2. Perform similarity search against ChromaDB
    3. Return documents with metadata

    Args:
        ticket_text: The raw ticket text.
        category: The classified category from the Triage Agent.
        k: Number of documents to retrieve (default: 5).

    Returns:
        List of dicts with 'content' and 'source' keys.
    """
    logger.info(f"Retrieving documents for category: {category}")

    # Step 1: Optimize the search query using the LLM
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

    # Step 2: Perform similarity search against ChromaDB
    docs = similarity_search(optimized_query, k=k)

    # Step 3: Format results with metadata
    results = []
    for doc in docs:
        results.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "unknown"),
        })

    logger.info(f"Retrieved {len(results)} document chunks")
    return results
