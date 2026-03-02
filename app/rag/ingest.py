"""
Document ingestion script for the RAG pipeline.

Reads all markdown files from the knowledge base directory, splits them
into overlapping chunks, embeds them via OpenAI, and stores them in
ChromaDB. Run this once to populate the vector store before using the
Retrieval Agent.

Usage:
    python -m app.rag.ingest

Why chunk + overlap?
- LLMs have context limits — we can't feed entire documents
- 500-char chunks capture a single concept/procedure
- 50-char overlap ensures we don't split mid-sentence at boundaries
"""

import os
import glob
import logging

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import settings
from app.rag.vectorstore import get_vectorstore

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

# Path to the knowledge base markdown files
KNOWLEDGE_BASE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "data",
    "knowledge_base",
)


def load_documents() -> list:
    """
    Load all markdown files from the knowledge base directory.

    Returns:
        List of LangChain Document objects with metadata.
    """
    documents = []
    md_files = glob.glob(os.path.join(KNOWLEDGE_BASE_DIR, "*.md"))

    if not md_files:
        logger.warning(f"No markdown files found in {KNOWLEDGE_BASE_DIR}")
        return documents

    for file_path in md_files:
        try:
            loader = TextLoader(file_path, encoding="utf-8")
            docs = loader.load()
            # Add source filename as metadata
            for doc in docs:
                doc.metadata["source"] = os.path.basename(file_path)
            documents.extend(docs)
            logger.info(f"Loaded: {os.path.basename(file_path)}")
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")

    return documents


def split_documents(documents: list) -> list:
    """
    Split documents into smaller chunks for embedding.

    Uses RecursiveCharacterTextSplitter which tries to split on
    natural boundaries (paragraphs, sentences, words) before
    resorting to character-level splitting.

    Args:
        documents: List of loaded Document objects.

    Returns:
        List of chunked Document objects.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
    return chunks


def ingest():
    """
    Main ingestion pipeline: load → split → embed → store in ChromaDB.
    """
    logger.info("Starting knowledge base ingestion...")

    # Step 1: Load documents
    documents = load_documents()
    if not documents:
        logger.error("No documents to ingest. Aborting.")
        return

    logger.info(f"Loaded {len(documents)} documents")

    # Step 2: Split into chunks
    chunks = split_documents(documents)

    # Step 3: Embed and store in ChromaDB
    logger.info("Embedding and storing chunks in ChromaDB...")
    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)

    logger.info(
        f"Ingestion complete! "
        f"Stored {len(chunks)} chunks in collection "
        f"'{settings.chroma_collection_name}'"
    )


if __name__ == "__main__":
    ingest()
