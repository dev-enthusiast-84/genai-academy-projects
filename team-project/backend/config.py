import os
from dotenv import load_dotenv
from typing import Dict, Any

load_dotenv(".env.local")


class Settings:
    """Configuration from TECHNICAL-ARCHITECTURE.md: ADR-2

    Per-Agent LLM Routing:
    - Strategist:  Kimi 3 primary → Claude fallback
    - Creator:     Claude 3.5 primary → Kimi 3 fallback
    - Reviewer:    Kimi 3 primary → Claude fallback
    """

    # LLM Provider APIs
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    KIMI_API_KEY = os.getenv("KIMI_API_KEY")

    # Per-agent model selection
    LLM_STRATEGIST_MODEL = os.getenv("LLM_STRATEGIST_MODEL", "kimi-3")
    LLM_STRATEGIST_FALLBACK = os.getenv("LLM_STRATEGIST_FALLBACK", "claude-3-5-sonnet-20241022")
    LLM_CREATOR_MODEL = os.getenv("LLM_CREATOR_MODEL", "claude-3-5-sonnet-20241022")
    LLM_CREATOR_FALLBACK = os.getenv("LLM_CREATOR_FALLBACK", "kimi-3")
    LLM_REVIEWER_MODEL = os.getenv("LLM_REVIEWER_MODEL", "kimi-3")
    LLM_REVIEWER_FALLBACK = os.getenv("LLM_REVIEWER_FALLBACK", "claude-3-5-sonnet-20241022")

    # LiteLLM configuration
    LITELLM_TIMEOUT_SECONDS = int(os.getenv("LITELLM_TIMEOUT_SECONDS", "30"))
    LITELLM_MAX_RETRIES = int(os.getenv("LITELLM_MAX_RETRIES", "3"))
    LITELLM_RATE_LIMIT = int(os.getenv("LITELLM_RATE_LIMIT", "10"))

    # Caching
    LLM_CACHE_ENABLED = os.getenv("LLM_CACHE_ENABLED", "true").lower() == "true"
    LLM_CACHE_TTL_SECONDS = int(os.getenv("LLM_CACHE_TTL_SECONDS", "3600"))

    # Vector database (Pinecone)
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-west-2")
    PINECONE_INDEX = os.getenv("PINECONE_INDEX", "content-embeddings")

    # Database (Supabase/PostgreSQL)
    DATABASE_URL = os.getenv("DATABASE_URL")
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    # Observability
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    POSTHOG_API_KEY = os.getenv("POSTHOG_API_KEY")

    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @staticmethod
    def get_agent_config(agent_name: str) -> Dict[str, Any]:
        """Get LiteLLM config for a specific agent"""
        config = {
            "timeout": Settings.LITELLM_TIMEOUT_SECONDS,
            "max_retries": Settings.LITELLM_MAX_RETRIES,
            "cache_enabled": Settings.LLM_CACHE_ENABLED,
            "cache_ttl": Settings.LLM_CACHE_TTL_SECONDS,
        }

        if agent_name == "strategist":
            config["model"] = Settings.LLM_STRATEGIST_MODEL
            config["fallback_models"] = [Settings.LLM_STRATEGIST_FALLBACK]
        elif agent_name == "creator":
            config["model"] = Settings.LLM_CREATOR_MODEL
            config["fallback_models"] = [Settings.LLM_CREATOR_FALLBACK]
        elif agent_name == "reviewer":
            config["model"] = Settings.LLM_REVIEWER_MODEL
            config["fallback_models"] = [Settings.LLM_REVIEWER_FALLBACK]

        return config


settings = Settings()
