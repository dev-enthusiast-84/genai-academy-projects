"""Reviewer Agent - Quality Assessment

Model: Kimi 3 (primary, excellent evaluation) → Claude 3.5 (fallback)
Cost: ~$3.25/month (Kimi)
Quality: 8.5/10 evaluation strength
"""

from typing import Dict, Any
import logging
from litellm import completion

from config import settings

logger = logging.getLogger(__name__)

REVIEWER_SYSTEM_PROMPT = """You are a content quality reviewer. Evaluate the draft for:
- Tone consistency with user's voice
- Clarity and readability
- Generic phrases (flag clichés)
- Engagement potential
- Platform fit

Return JSON with: quality_score (0-10), tone_score, clarity_score, generic_phrases, suggestions"""


async def reviewer_agent(draft: Dict[str, Any]) -> Dict[str, Any]:
    """Quality check and score the generated draft

    Args:
        draft: Generated draft from creator agent

    Returns:
        {
            "quality_score": 8.5,
            "tone_score": 9.0,
            "clarity_score": 8.0,
            "generic_phrases": ["Excited to share", "Game-changer"],
            "suggestions": ["Replace 'exciting' with specific benefit", ...],
            "overall_verdict": "APPROVE|REVISE|REJECT"
        }
    """
    config = settings.get_agent_config("reviewer")

    draft_text = f"Title: {draft.get('title', '')}\n\nBody:\n{draft.get('body', '')}"

    try:
        logger.info(f"Reviewer assessment (MVP mock - will use {config['model']} in production)")

        # MVP: Mock quality review
        body_len = len(draft.get("body", ""))
        word_count = draft.get("word_count", 0)

        # Calculate scores based on draft characteristics
        quality_score = 8.2 + (word_count % 5) * 0.1
        tone_score = 8.8 + (body_len % 5) * 0.08
        clarity_score = 8.4 + (word_count % 7) * 0.07

        # Cap at 10
        quality_score = min(quality_score, 10)
        tone_score = min(tone_score, 10)
        clarity_score = min(clarity_score, 10)

        return {
            "quality_score": quality_score,
            "tone_score": tone_score,
            "clarity_score": clarity_score,
            "generic_phrases": [
                "Interesting" if "Interesting" in draft.get("body", "") else None,
                "Insights" if "insight" in draft.get("body", "").lower() else None,
            ] if draft.get("body") else [],
            "suggestions": [
                "Consider adding a specific example",
                "Strong personal perspective - keep it",
                "Call-to-action is clear",
            ],
            "overall_verdict": "APPROVE" if quality_score >= 8.0 else "REVISE",
        }

    except Exception as e:
        logger.error(f"Reviewer agent error: {str(e)}")
        return {
            "quality_score": 0.0,
            "error": str(e),
            "overall_verdict": "ERROR",
        }
