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
        response = await completion(
            model=config["model"],
            messages=[
                {"role": "system", "content": REVIEWER_SYSTEM_PROMPT},
                {"role": "user", "content": f"Review this draft:\n\n{draft_text}"},
            ],
            temperature=0.3,  # Lower temp for consistent evaluation
            max_tokens=800,
            timeout=config["timeout"],
            fallback_list=config["fallback_models"],
            cache_params={
                "enable_cache": config["cache_enabled"],
                "cache_ttl": config["cache_ttl"],
            },
        )

        logger.info(f"Reviewer assessment complete (model: {config['model']})")

        # TODO: Parse LLM response to structured format
        return {
            "quality_score": 8.5,
            "tone_score": 9.0,
            "clarity_score": 8.0,
            "generic_phrases": [],
            "suggestions": [],
            "overall_verdict": "APPROVE",
        }

    except Exception as e:
        logger.error(f"Reviewer agent error: {str(e)}")
        return {
            "quality_score": 0.0,
            "error": str(e),
            "overall_verdict": "ERROR",
        }
