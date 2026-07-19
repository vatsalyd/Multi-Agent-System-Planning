"""
Triage Agent — classifies tickets using Groq (LLaMA 3.3 70B).
"""

import json

from langchain_core.messages import SystemMessage, HumanMessage

from app.llm.provider import create_llm
from app.logging_config import get_logger

logger = get_logger(__name__)

CATEGORIES = [
    "IT_SUPPORT",
    "HR_POLICY",
    "EXPENSE",
    "ONBOARDING",
    "GENERAL",
]

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


async def triage_ticket(ticket_text: str) -> dict:
    """Classify an incoming ticket into a category."""
    logger.info("Triaging ticket: %s...", ticket_text[:100])

    llm = create_llm(temperature=0.0)
    messages = [
        SystemMessage(content=TRIAGE_SYSTEM_PROMPT),
        HumanMessage(content=f"Classify this ticket:\n\n{ticket_text}"),
    ]

    response = await llm.ainvoke(messages)

    # Strip markdown code fences if model wraps JSON in ```json ... ```
    raw = response.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        result = json.loads(raw)
        if result.get("category") not in CATEGORIES:
            logger.warning(
                "Unknown category '%s', defaulting to GENERAL",
                result.get("category"),
            )
            result["category"] = "GENERAL"
            result["confidence"] = 0.3

        logger.info(
            "Triage result: %s (confidence: %s)",
            result["category"],
            result["confidence"],
        )
        return result

    except (json.JSONDecodeError, KeyError) as e:
        logger.error("Failed to parse triage response: %s", e)
        return {
            "category": "GENERAL",
            "confidence": 0.0,
            "summary": "Failed to classify ticket",
        }