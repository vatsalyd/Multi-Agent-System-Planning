"""
Triage Agent — the "receptionist" of the system.

This agent receives a raw incoming ticket and classifies its intent into
one of the predefined categories. It uses OpenAI's structured output
(function calling) to return a consistent JSON schema with the category,
a confidence score, and a brief summary.

Why structured output?
- Guarantees a parseable JSON response (no regex/string parsing needed)
- Enforces the exact schema we need downstream
- Category is constrained to a known set — prevents hallucinated categories
"""

import json
import logging

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.config import settings

logger = logging.getLogger(__name__)

# The categories the Triage Agent can classify into
CATEGORIES = [
    "IT_SUPPORT",
    "HR_POLICY",
    "EXPENSE",
    "ONBOARDING",
    "GENERAL",
]

# System prompt for the Triage Agent
TRIAGE_SYSTEM_PROMPT = """You are a corporate ticket triage specialist. Your job is to classify incoming employee support tickets into the correct category.

Available categories:
- IT_SUPPORT: Password resets, VPN issues, software installation, hardware problems, network issues, account lockouts
- HR_POLICY: Leave requests, benefits questions, attendance, workplace policies, parental leave
- EXPENSE: Expense reports, reimbursement questions, travel expenses, receipt submissions
- ONBOARDING: New employee setup, orientation, first-week questions, access requests for new hires
- GENERAL: Anything that doesn't clearly fit the above categories, general FAQs, office questions

You MUST respond with a valid JSON object containing exactly these fields:
{
    "category": "<one of: IT_SUPPORT, HR_POLICY, EXPENSE, ONBOARDING, GENERAL>",
    "confidence": <float between 0.0 and 1.0>,
    "summary": "<one-sentence summary of the ticket>"
}

Rules:
- Choose the MOST specific category that applies
- Set confidence based on how clearly the ticket matches the category
- The summary should be concise (max 20 words)
- Respond ONLY with the JSON object, no additional text"""


def create_triage_agent() -> ChatOpenAI:
    """Create the LLM instance for the Triage Agent."""
    return ChatOpenAI(
        model=settings.openai_model,
        openai_api_key=settings.openai_api_key,
        temperature=0.0,  # Deterministic classification
    )


def triage_ticket(ticket_text: str) -> dict:
    """
    Classify an incoming ticket into a category.

    Args:
        ticket_text: The raw text of the incoming support ticket.

    Returns:
        dict with keys: category, confidence, summary
    """
    logger.info(f"Triaging ticket: {ticket_text[:100]}...")

    llm = create_triage_agent()

    messages = [
        SystemMessage(content=TRIAGE_SYSTEM_PROMPT),
        HumanMessage(content=f"Classify this ticket:\n\n{ticket_text}"),
    ]

    response = llm.invoke(messages)

    try:
        result = json.loads(response.content)
        # Validate the category
        if result.get("category") not in CATEGORIES:
            logger.warning(
                f"Unknown category '{result.get('category')}', "
                f"defaulting to GENERAL"
            )
            result["category"] = "GENERAL"
            result["confidence"] = 0.3

        logger.info(
            f"Triage result: {result['category']} "
            f"(confidence: {result['confidence']})"
        )
        return result

    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to parse triage response: {e}")
        return {
            "category": "GENERAL",
            "confidence": 0.0,
            "summary": "Failed to classify ticket",
        }
