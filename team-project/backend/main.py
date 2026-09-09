"""Content Strategist MVP Backend

LLM Configuration (TECHNICAL-ARCHITECTURE.md: ADR-2):
- Strategist:  Kimi 3 (primary) → Claude 3.5 (fallback)
- Creator:     Claude 3.5 (primary) → Kimi 3 (fallback)
- Reviewer:    Kimi 3 (primary) → Claude 3.5 (fallback)

All LLM calls use LiteLLM abstraction with automatic fallback, caching, and cost tracking.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

from config import settings
from agents import strategist_agent, creator_agent, reviewer_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Content Strategist MVP",
    description="AI system for content strategy, generation, and review",
    version="0.1.0",
)

# CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class AnalyzeRequest(BaseModel):
    content: str
    content_type: str = "linkedin"


class AnalyzeResponse(BaseModel):
    action: str
    reasoning: str
    confidence: float


class HealthResponse(BaseModel):
    status: str
    version: str
    dependencies: dict


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint - verify API keys and dependencies"""
    dependencies = {
        "claude": "✓" if settings.ANTHROPIC_API_KEY or settings.OPENROUTER_API_KEY else "✗",
        "kimi": "✓" if settings.KIMI_API_KEY else "✗",
        "pinecone": "✓" if settings.PINECONE_API_KEY else "✗",
        "database": "✓" if settings.DATABASE_URL else "✗",
    }
    all_healthy = all(v == "✓" for v in dependencies.values())
    return {
        "status": "healthy" if all_healthy else "degraded",
        "version": "0.1.0",
        "dependencies": dependencies,
        "llm_config": {
            "strategist_model": settings.LLM_STRATEGIST_MODEL,
            "strategist_fallback": settings.LLM_STRATEGIST_FALLBACK,
            "creator_model": settings.LLM_CREATOR_MODEL,
            "creator_fallback": settings.LLM_CREATOR_FALLBACK,
            "reviewer_model": settings.LLM_REVIEWER_MODEL,
            "reviewer_fallback": settings.LLM_REVIEWER_FALLBACK,
        },
    }


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """Analyze content and recommend repurposing strategy

    Uses Strategist Agent (Kimi 3 primary → Claude 3.5 fallback)
    """
    logger.info(f"Analyzing content ({len(request.content)} chars)...")

    try:
        result = await strategist_agent(request.content)
        logger.info(f"Analysis complete: {result.get('action')}")
        return result
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/create-draft")
async def create_draft(request: dict):
    """Create draft based on approved recommendation

    Uses Creator Agent (Claude 3.5 primary → Kimi 3 fallback)
    Maintains user voice consistency
    """
    strategy = request.get("strategy", {})
    voice_samples = request.get("voice_samples", [])

    logger.info(f"Creating draft (action: {strategy.get('action')})")

    try:
        draft = await creator_agent(strategy, voice_samples)
        logger.info(f"Draft created: {draft.get('word_count')} words")
        return draft
    except Exception as e:
        logger.error(f"Draft creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/review")
async def review(draft: dict):
    """Quality check and score the draft

    Uses Reviewer Agent (Kimi 3 primary → Claude 3.5 fallback)
    Evaluates tone, clarity, engagement, and generic phrases
    """
    logger.info(f"Reviewing draft: {draft.get('title', '')[:50]}...")

    try:
        review_result = await reviewer_agent(draft)
        logger.info(f"Review complete: quality_score={review_result.get('quality_score')}")
        return review_result
    except Exception as e:
        logger.error(f"Review failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """API root - Content Strategist MVP Backend"""
    return {
        "name": "Content Strategist MVP API",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "health": "GET /health - System status and LLM config",
            "analyze": "POST /analyze - Strategist agent (content analysis)",
            "create_draft": "POST /create-draft - Creator agent (draft generation)",
            "review": "POST /review - Reviewer agent (quality assessment)",
        },
        "llm_routing": {
            "strategist": "Kimi 3 → Claude 3.5",
            "creator": "Claude 3.5 → Kimi 3",
            "reviewer": "Kimi 3 → Claude 3.5",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
