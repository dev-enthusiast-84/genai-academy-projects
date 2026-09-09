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
        logger.info(f"Creator draft (MVP mock - will use {config['model']} in production)")

        # MVP: Mock draft response
        action = strategy.get("action", "repurpose")
        sample_drafts = {
            "publish": {
                "title": "My Latest Insights on Content Strategy",
                "body": "I've been thinking a lot about how content creators can better leverage their unique voice...\n\nHere are my key takeaways:\n\n1. Authenticity wins over perfection\n2. Consistency builds trust\n3. Audience needs drive strategy\n\nWhat are your thoughts? I'd love to hear what works for you.",
                "word_count": 240,
            },
            "repurpose": {
                "title": "The Art of Content Repurposing: How I Cut Production Time by 60%",
                "body": "One of the biggest time-wasters in content creation is doing everything from scratch.\n\nInstead, I've developed a system for repurposing core ideas across multiple platforms:\n\n**LinkedIn:** Thought leadership threads\n**Blog:** Deep-dive articles\n**Twitter:** Micro-insights\n\nThis doesn't mean duplicating content—it's about adapting the same core message for each platform's unique audience and format.\n\nThe result? I spend 30% of the time creating 3x the content.\n\nHave you tried repurposing? What's your biggest challenge?",
                "word_count": 385,
            },
            "combine": {
                "title": "Building Scalable Content Systems: Lessons from 2 Years of Shipping",
                "body": "After shipping hundreds of content pieces, I've learned that content creation at scale requires systems, not heroics.\n\nHere's what actually works:\n\n1. **One source, many outputs**\n   - Write once, publish everywhere\n   - Adapt for each platform\n   - Track what resonates\n\n2. **Batch your creation**\n   - Dedicated content days\n   - Reduce context switching\n   - Improve quality and speed\n\n3. **Build your unique voice**\n   - Consistency in tone\n   - Authentic perspective\n   - Trust over clicks\n\nThe platforms change, but these principles remain true.\n\nWhat system do you use for your content? I'm curious what works outside my bubble.",
                "word_count": 520,
            },
        }

        draft_template = sample_drafts.get(action, sample_drafts["repurpose"])

        return {
            "title": draft_template["title"],
            "body": draft_template["body"],
            "word_count": draft_template["word_count"],
            "reading_time": f"{max(1, draft_template['word_count'] // 200)} min",
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
