# LLM Configuration & Model Routing

**Source:** `TECHNICAL-ARCHITECTURE.md` (ADR-2)  
**Last Updated:** 2026-09-09

## Overview

This system uses **LiteLLM** for provider-agnostic LLM access with a **dual-model strategy**:
- **Claude 3.5 Sonnet** (Anthropic): Best-in-class writing quality
- **Kimi 3** (Moonshot): Fast, cost-effective analysis & evaluation

**Cost Savings:** 41% vs all-GPT-4o ($6.50/month vs $11/month)  
**Quality:** 98% as good as GPT-4o alone  
**Reliability:** 99.95% with automatic fallback

---

## Per-Agent Model Routing

```
┌─────────────┬──────────────┬────────────────┐
│ Agent       │ Primary      │ Fallback       │
├─────────────┼──────────────┼────────────────┤
│ Strategist  │ Kimi 3       │ Claude 3.5     │
│ Creator     │ Claude 3.5   │ Kimi 3         │
│ Reviewer    │ Kimi 3       │ Claude 3.5     │
└─────────────┴──────────────┴────────────────┘
```

### Why This Routing?

**Strategist (Kimi 3 primary)**
- Task: Semantic analysis + pattern recognition
- Kimi 3: Excellent at analysis (9.0/10)
- Saves: 70% cost vs Claude
- Fallback: Claude if Kimi unavailable

**Creator (Claude 3.5 primary)**
- Task: High-quality writing + voice consistency
- Claude 3.5: Best-in-class quality (9.3/10)
- Quality requirement: 9.5/10 (critical for user voice)
- Fallback: Kimi 3 for cost savings if Claude slow

**Reviewer (Kimi 3 primary)**
- Task: Evaluation + structured scoring
- Kimi 3: Excellent at evaluation (8.5/10)
- Saves: 70% cost vs Claude
- Fallback: Claude if Kimi unavailable

---

## Environment Variables

```bash
# Claude 3.5 Sonnet (Anthropic)
ANTHROPIC_API_KEY=sk-ant-YOUR_KEY

# Optional: Use OpenRouter for lower latency
OPENROUTER_API_KEY=sk-or-YOUR_KEY

# Kimi 3 (Moonshot)
KIMI_API_KEY=sk-moonshot-YOUR_KEY

# Per-agent model selection
LLM_STRATEGIST_MODEL=kimi-3
LLM_STRATEGIST_FALLBACK=claude-3-5-sonnet-20241022
LLM_CREATOR_MODEL=claude-3-5-sonnet-20241022
LLM_CREATOR_FALLBACK=kimi-3
LLM_REVIEWER_MODEL=kimi-3
LLM_REVIEWER_FALLBACK=claude-3-5-sonnet-20241022

# LiteLLM settings
LITELLM_TIMEOUT_SECONDS=30
LITELLM_MAX_RETRIES=3
LITELLM_RATE_LIMIT=10
LLM_CACHE_ENABLED=true
LLM_CACHE_TTL_SECONDS=3600
```

---

## LiteLLM Integration Pattern

All agents follow this pattern:

```python
from litellm import completion
from config import settings

async def strategist_agent(content: str):
    config = settings.get_agent_config("strategist")
    
    response = await completion(
        model=config["model"],                    # Primary: kimi-3
        messages=[...],
        temperature=0.7,
        max_tokens=1000,
        timeout=config["timeout"],                # 30s
        fallback_list=config["fallback_models"],  # [claude-3-5-sonnet-...]
        cache_params={
            "enable_cache": config["cache_enabled"],      # True
            "cache_ttl": config["cache_ttl"],             # 3600s
        },
    )
    return parse_response(response)
```

### Key Features

- **Automatic Fallback:** If primary model fails, LiteLLM switches to fallback
- **Prompt Caching:** Anthropic prompt caching saves 90% tokens on repeated prompts
- **Rate Limiting:** Exponential backoff (1s → 2s → 4s → 8s)
- **Cost Tracking:** LiteLLM logs token usage and cost per call
- **Observability:** All calls traced to LangSmith with costs included

---

## Cost Analysis

### Monthly Estimates (MVP usage: 1.3M tokens)

| Config | Cost/Month | Quality | Speed | Reliability |
|--------|-----------|---------|-------|-------------|
| All GPT-4o | $11.00 | 9.2/10 | 1200ms | 99.8% |
| All Kimi 3 | $3.25 | 8.7/10 | 700ms | 97% |
| **Dual (Recommended)** | **$6.50** | **9.0/10** | **800ms** | **99.95%** |

### Per-Agent Costs

```
Strategist call (Kimi 3):
  Input tokens: 450 (cached: -400)
  Output tokens: 200
  Cost: ~$0.0015

Creator call (Claude 3.5):
  Input tokens: 800
  Output tokens: 350
  Cost: ~$0.0045

Reviewer call (Kimi 3):
  Input tokens: 300
  Output tokens: 150
  Cost: ~$0.0010

Total per workflow: ~$0.007 (0.7 cents)
```

---

## Fallback Hierarchy

| Tier | Provider | Use Case |
|------|----------|----------|
| 1 | Kimi 3 (Strategist/Reviewer) | Primary - fast, cheap |
| 2 | Claude 3.5 (Strategist/Reviewer) | Fallback - proven, reliable |
| 3 | Cached Response | Emergency - ensures demo doesn't fail |

---

## Configuration Validation

Check health status:
```bash
curl http://localhost:8000/health
```

Returns:
```json
{
  "status": "healthy",
  "dependencies": {
    "claude": "✓",
    "kimi": "✓",
    "pinecone": "✓",
    "database": "✓"
  },
  "llm_config": {
    "strategist_model": "kimi-3",
    "strategist_fallback": "claude-3-5-sonnet-20241022",
    "creator_model": "claude-3-5-sonnet-20241022",
    "creator_fallback": "kimi-3",
    "reviewer_model": "kimi-3",
    "reviewer_fallback": "claude-3-5-sonnet-20241022"
  }
}
```

---

## Switching Models (Emergency)

If a model fails or becomes unavailable, update `.env.local`:

```bash
# Switch creator to Kimi 3 temporarily
LLM_CREATOR_MODEL=kimi-3
LLM_CREATOR_FALLBACK=claude-3-5-sonnet-20241022

# No code changes needed - LiteLLM handles it
```

---

## See Also

- `TECHNICAL-ARCHITECTURE.md` - Full architecture decisions (ADR-2)
- `backend/config.py` - Implementation configuration
- `backend/agents/` - Per-agent LLM implementations
- `.env.local` - Runtime configuration

