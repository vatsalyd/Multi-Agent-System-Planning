"""
Retrieval Agent — optimizes search queries and retrieves docs from Pinecone.
"""

from langchain_core.messages import SystemMessage, HumanMessage

from app.llm.provider import create_llm
from app.rag.vectorstore import similarity_search, RetrievedChunk
from app.logging_config import get_logger

logger = get_logger(__name__)

RETRIEVAL_SYSTEM_PROMPT = """You are a search query optimization specialist. Given a support ticket and its classified category, your job is to generate an optimized search query that will retrieve the most relevant company policy documents.

Rules:
- Extract the core question or problem from the ticket
- Include relevant keywords related to the category
- Remove filler words and irrelevant details
- The query should be 10-20 words maximum
- Respond with ONLY the optimized search query, nothing else"""


async def retrieve_documents(
    ticket_text: str, category: str, k: int = 5
) -> list[RetrievedChunk]:
    """Optimize the search query via LLM, then retrieve relevant docs from ChromaDB."""
    logger.info("Retrieving documents for category: %s", category)

    llm = create_llm(temperature=0.0)
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
    response = await llm.ainvoke(messages)
    optimized_query = response.content.strip()
    logger.info("Optimized search query: %s", optimized_query)

    results = similarity_search(optimized_query, k=k)

    logger.info("Retrieved %d document chunks", len(results))
    return results