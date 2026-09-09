## Purpose

Defines LLM provider abstraction and configuration strategy for multi-provider support and failover resilience.

## ADDED Requirements

### Requirement: LLM provider abstraction
The system SHALL use LiteLLM as unified interface for all LLM calls, supporting multiple providers with automatic fallback.

#### Scenario: Primary provider (Claude)
- **WHEN** agent makes LLM call
- **THEN** system routes through LiteLLM
- **AND** uses Claude 3.5 Sonnet as primary model
- **AND** supports both OpenRouter and direct Anthropic API

#### Scenario: Automatic fallback to GPT-4
- **WHEN** Claude API is unavailable or rate-limited
- **THEN** LiteLLM automatically retries with GPT-4-Turbo
- **AND** call succeeds without user intervention
- **AND** response quality remains consistent

#### Scenario: Provider switching via environment variable
- **WHEN** deployment uses different provider (during demo or incident)
- **THEN** changing `LLM_MODEL` environment variable switches provider
- **AND** no code changes required
- **AND** all agents continue working with new provider

### Requirement: Rate limiting and cost tracking
The system SHALL implement built-in rate limiting and track LLM costs.

#### Scenario: Automatic backoff on rate limit
- **WHEN** LLM provider returns rate limit error
- **THEN** LiteLLM automatically backs off and retries
- **AND** backoff time increases exponentially (1s → 2s → 4s → 8s)
- **AND** succeeds after retry without user error

#### Scenario: Cost tracking per call
- **WHEN** agent makes LLM call
- **THEN** LiteLLM logs token usage and cost
- **AND** cost metadata included in observability traces (LangSmith)
- **AND** system operator can monitor total costs

### Requirement: Response caching for efficiency
The system SHALL cache LLM responses to reduce API calls and latency.

#### Scenario: Prompt caching
- **WHEN** system prompt is used repeatedly (same prompt, different inputs)
- **THEN** system caches system prompt and reuses across calls
- **AND** saves 90% of tokens on system prompt (Anthropic prompt caching)
- **AND** reduces latency and cost significantly

#### Scenario: Response caching for demo scenarios
- **WHEN** demo runs multiple times with same content
- **THEN** system can cache Strategist recommendations for 3-5 demo scenarios
- **AND** fallback to cached response if Claude API fails during demo
- **AND** Demo continues without showing API errors

## IMPLEMENTATION DETAIL: LiteLLM Configuration

### Environment Variables (.env)
```bash
# Primary LLM Provider
LLM_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=sk-ant-...

# Fallback Provider
FALLBACK_MODEL=gpt-4-turbo
OPENAI_API_KEY=sk-...

# Optional: LiteLLM Cloud Proxy (for production)
# LITELLM_PROXY_URL=https://proxy.litellm.ai
# LITELLM_PROXY_KEY=...

# Rate Limiting
LLM_RATE_LIMIT=10  # max requests per minute
LLM_MAX_RETRIES=3
LLM_TIMEOUT_SECONDS=30

# Caching
LLM_CACHE_ENABLED=true
LLM_CACHE_TTL_SECONDS=3600  # 1 hour
```

### Agent Configuration Pattern
```python
# All agents use this pattern:
from litellm import completion
from config import get_llm_config

async def strategist_agent(content: str) -> Recommendation:
    config = get_llm_config()
    
    response = await completion(
        model=config['model'],
        messages=[
            {"role": "system", "content": STRATEGIST_PROMPT},
            {"role": "user", "content": f"Analyze: {content}"}
        ],
        temperature=0.7,
        max_tokens=1000,
        timeout=config['timeout'],
        fallback_list=config['fallback_models'],
        cache_params={
            "enable_cache": True,
            "cache_ttl": config['cache_ttl']
        }
    )
    
    return parse_recommendation(response)
```

### Provider Comparison

| Provider | Cost | Latency | Quality | Availability | Fallback |
|----------|------|---------|---------|--------------|----------|
| Claude 3.5 Sonnet (Primary) | $3/$15 per 1M | 200-500ms | Excellent | 99.9% | GPT-4 |
| GPT-4 Turbo (Fallback) | $10/$30 per 1M | 150-400ms | Excellent | 99.95% | Gemini |
| Gemini Pro (3rd tier) | $0.5/$1.5 per 1M | 300-600ms | Good | 99.8% | Llama |

### Cost Tracking Example
```
Strategist call: 
  Input tokens: 450 (cached: -400)
  Output tokens: 200
  Cost: $0.0015
  Trace: https://smith.langchain.com/trace/...

Creator call:
  Input tokens: 800
  Output tokens: 350
  Cost: $0.0045
  Trace: https://smith.langchain.com/trace/...

Total Session Cost: $0.0060
```

## IMPLEMENTATION DETAIL: Fallback Strategy

### Tier 1: Claude 3.5 Sonnet (Primary)
- Use OpenRouter for lower latency (US-based)
- Fallback to direct Anthropic API if OpenRouter down
- Timeout: 30 seconds

### Tier 2: GPT-4 Turbo (Fallback)
- Use OpenAI API directly
- Triggers if Claude fails or rate-limited
- Timeout: 25 seconds

### Tier 3: Gemini Pro (3rd tier, Phase 2)
- Use Google Generative AI API
- Triggers if both Claude and GPT fail
- Lower quality but ensures demo doesn't fail

### Tier 4: Cached Response (Emergency)
- Last resort: return pre-computed response for demo scenario
- Ensures demo works even if all APIs are down
- Clearly labeled: "Using cached demo response"

## Phase 2: Advanced Configuration

- Fine-tuned models specific to user's content domain
- Router-based provider selection based on cost/quality/latency
- Automatic A/B testing of models
- Cost optimization per agent (e.g., Reviewe uses cheaper model than Strategist)
