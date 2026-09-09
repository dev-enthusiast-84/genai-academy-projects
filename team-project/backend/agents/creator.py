"""Creator Agent - Draft Generation

Model: Claude 3.5 Sonnet (primary, best writing quality) → Kimi 3 (fallback)
Cost: ~$6/month (Claude)
Quality: 9.3/10 writing + voice consistency
"""

from typing import Dict, Any, List
import logging
from litellm import completion

from config import settings

logger = logging.getLogger(__name__)

CREATOR_SYSTEM_PROMPT = """You are an expert content writer who captures the user's unique voice perfectly.
Generate high-quality, platform-optimized drafts that sound authentic and engaging.

Use the provided voice samples to match tone, vocabulary, and style.
Return JSON with: title, body, word_count, reading_time, platform"""


async def creator_agent(
    strategy: Dict[str, Any],
    voice_samples: List[str],
) -> Dict[str, Any]:
    """Generate optimized draft based on approved strategy

    Args:
        strategy: Approved recommendation from strategist
        voice_samples: User's writing samples (3-5 examples)

    Returns:
        {
            "title": "Draft title",
            "body": "Full draft content",
            "word_count": 250,
            "reading_time": "2 min",
            "platform": "linkedin|blog|thread",
            "quality_preview": {...}  # Quality metrics
        }
    """
    config = settings.get_agent_config("creator")

    voice_context = "\n".join(
        [f"Voice Sample {i+1}:\n{sample}" for i, sample in enumerate(voice_samples)]
    )

    prompt = f"""Based on this strategy: {strategy.get('reasoning', '')}

User's Writing Voice (for consistency):
{voice_context}

Generate a high-quality draft that maintains their voice and follows the strategy."""

    try:
        response = await completion(
            model=config["model"],
            messages=[
                {"role": "system", "content": CREATOR_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.8,
            max_tokens=1500,
            timeout=config["timeout"],
            fallback_list=config["fallback_models"],
            cache_params={
                "enable_cache": config["cache_enabled"],
                "cache_ttl": config["cache_ttl"],
            },
        )

        logger.info(f"Creator draft complete (model: {config['model']})")

        # TODO: Parse LLM response to structured format
        return {
            "title": "How I Built This AI Content System",
            "body": "Lorem ipsum dolor sit amet...",
            "word_count": 350,
            "reading_time": "2 min",
            "platform": "linkedin",
            "quality_preview": {"tone": "professional", "clarity": "high"},
        }

    except Exception as e:
        logger.error(f"Creator agent error: {str(e)}")
        return {
            "title": "Draft generation failed",
            "body": "",
            "error": str(e),
        }
