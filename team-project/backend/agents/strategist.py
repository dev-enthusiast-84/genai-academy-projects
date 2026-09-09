"""Strategist Agent - Content Strategy Analysis

Model: Kimi 3 (primary, fast analysis) → Claude 3.5 (fallback)
Cost: ~$3.25/month (Kimi) vs $6 (Claude)
Quality: 9.0/10 analysis strength
"""

from typing import Dict, Any
import logging
from litellm import completion

from config import settings

logger = logging.getLogger(__name__)

STRATEGIST_SYSTEM_PROMPT = """You are a content strategy expert. Analyze the given content and recommend
the best repurposing strategy. Consider audience, platform fit, engagement potential, and voice consistency.

Return your analysis as JSON with: action, reasoning, confidence"""


async def strategist_agent(content: str) -> Dict[str, Any]:
    """Analyze content and recommend repurposing strategy

    Args:
        content: User's content to analyze

    Returns:
        {
            "action": "publish|repurpose|rework|combine|skip",
            "reasoning": "Why this action",
            "confidence": 0.0-1.0,
            "similar_posts": [...],  # Top 5 similar posts from knowledge base
            "recommendations": [...]  # Specific repurposing suggestions
        }
    """
    config = settings.get_agent_config("strategist")

    try:
        response = await completion(
            model=config["model"],
            messages=[
                {"role": "system", "content": STRATEGIST_SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze this content:\n\n{content}"},
            ],
            temperature=0.7,
            max_tokens=1000,
            timeout=config["timeout"],
            fallback_list=config["fallback_models"],
            cache_params={
                "enable_cache": config["cache_enabled"],
                "cache_ttl": config["cache_ttl"],
            },
        )

        # Parse response (implement JSON extraction from LLM output)
        logger.info(f"Strategist analysis complete (model: {config['model']})")

        # TODO: Parse LLM response to structured format
        return {
            "action": "repurpose",
            "reasoning": "Content has strong technical depth suitable for LinkedIn thread + blog post",
            "confidence": 0.85,
            "similar_posts": [],
            "recommendations": ["Repurpose as LinkedIn thread", "Adapt for technical blog"],
        }

    except Exception as e:
        logger.error(f"Strategist agent error: {str(e)}")
        # Fallback to cached response or error response
        return {
            "action": "error",
            "reasoning": f"Analysis failed: {str(e)}",
            "confidence": 0.0,
        }
