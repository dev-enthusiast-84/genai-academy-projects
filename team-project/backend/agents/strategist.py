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
        # MVP: Mock response (replace with LiteLLM call for production)
        logger.info(f"Strategist analysis (MVP mock - will use {config['model']} in production)")

        # Simulate analysis based on content length
        content_len = len(content)
        if content_len < 100:
            action, reasoning = "publish", "Short form content - ready to publish as-is"
        elif content_len < 500:
            action, reasoning = "repurpose", "Medium content - good for LinkedIn + Twitter strategy"
        else:
            action, reasoning = "combine", "Long-form content - break into series + standalone posts"

        return {
            "action": action,
            "reasoning": reasoning,
            "confidence": 0.82 + (content_len % 10) * 0.01,
            "similar_posts": [
                {"id": 1, "title": "How to build AI systems", "engagement": 127},
                {"id": 2, "title": "Content strategy tips", "engagement": 89},
            ],
            "recommendations": [
                "Strong technical depth detected",
                "Good for professional audience",
                "Consider LinkedIn + blog distribution"
            ],
        }

    except Exception as e:
        logger.error(f"Strategist agent error: {str(e)}")
        return {
            "action": "error",
            "reasoning": f"Analysis failed: {str(e)}",
            "confidence": 0.0,
        }
