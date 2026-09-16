"""LLM agent client with tool support for investigation and review."""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable


class ModelError(Exception):
    """Raised when LLM requests fail."""
    pass


def settings(env_file: Path) -> Dict[str, Any]:
    """Load agent settings from .env file.

    Args:
        env_file: Path to .env file

    Returns:
        Settings dictionary
    """
    config = {
        'provider': os.getenv('LLM_PROVIDER', 'litellm'),
        'base_url': os.getenv('LITELLM_BASE_URL', 'http://127.0.0.1:4000/v1'),
        'api_key': os.getenv('LITELLM_API_KEY', 'default-key'),
        'litellm_base_url': os.getenv('LITELLM_BASE_URL', 'http://127.0.0.1:4000'),
        'litellm_api_key': os.getenv('LITELLM_API_KEY', 'default-key'),
        'openrouter_api_key': os.getenv('OPENROUTER_API_KEY', ''),
        'investigator_model': os.getenv('LLM_INVESTIGATOR_MODEL', 'ollama/phi'),
        'scope_reviewer_model': os.getenv('LLM_SCOPE_REVIEWER_MODEL', 'ollama/orca-mini'),
        'judge_model': os.getenv('LLM_JUDGE_MODEL', 'ollama/phi'),
        'auditor_model': os.getenv('LLM_AUDITOR_MODEL', 'ollama/phi'),
    }
    return config


class ModelClient:
    """Client for communicating with LLM providers (LiteLLM, OpenRouter)."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        provider: str = "litellm",
    ):
        """Initialize model client.

        Args:
            base_url: API endpoint URL
            api_key: API key for authentication
            model: Model ID (e.g., "ollama/phi")
            provider: Provider type (litellm, openrouter)
        """
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.provider = provider

    def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1600,
    ) -> Dict[str, Any]:
        """Request LLM completion with optional tool use.

        Args:
            messages: Message history in OpenAI format
            tools: Optional tool definitions
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Response with message and optional tool_calls

        Raises:
            ModelError: If request fails
        """
        try:
            import requests
        except ImportError:
            raise ModelError("requests library required. pip install requests")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        # Provider-specific options
        if self.provider == "openrouter":
            payload["provider"] = {"require_parameters": True}

        try:
            response = requests.post(
                f"{self.base_url.rstrip('/')}/chat/completions",
                json=payload,
                headers=headers,
                timeout=45,
            )
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            if hasattr(e.response, "status_code"):
                raise ModelError(
                    f"Provider returned HTTP {e.response.status_code}. "
                    "Check key, model access, and quota."
                )
            raise ModelError(
                "Cannot reach the provider. Check connection, HTTPS, and proxy."
            )
        except json.JSONDecodeError:
            raise ModelError("Provider returned invalid JSON.")

        choice = data.get("choices", [{}])[0]
        message = choice.get("message", {})

        if not message:
            raise ModelError("Provider returned no message")

        return message

    def models(self) -> List[Dict[str, Any]]:
        """List available models from provider.

        Returns:
            List of available models

        Raises:
            ModelError: If request fails
        """
        try:
            import requests
        except ImportError:
            raise ModelError("requests library required")

        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.get(
                f"{self.base_url.rstrip('/')}/models",
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", [])
        except Exception as e:
            raise ModelError(f"Failed to list models: {str(e)}")


# Tool definitions for agents
INVESTIGATOR_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "discover_records",
            "description": "Discover authorized record metadata. Empty query lists all records.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search filter (ID, title, service, kind)",
                    }
                },
                "required": ["query"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "trace_lineage",
            "description": "Trace explicit dependencies for a root record.",
            "parameters": {
                "type": "object",
                "properties": {
                    "root_id": {
                        "type": "string",
                        "description": "Root record ID to trace from",
                    }
                },
                "required": ["root_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "inspect_service",
            "description": "Check current presence and version of a record.",
            "parameters": {
                "type": "object",
                "properties": {
                    "record_id": {
                        "type": "string",
                        "description": "Record ID to inspect",
                    }
                },
                "required": ["record_id"],
                "additionalProperties": False,
            },
        },
    },
]

REVIEWER_TOOLS = []  # Reviewers use reasoning only

JUDGE_TOOLS = []  # Judges use reasoning only

AUDITOR_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "inspect_service",
            "description": "Verify current state of a record (verification only).",
            "parameters": {
                "type": "object",
                "properties": {
                    "record_id": {
                        "type": "string",
                        "description": "Record ID to verify",
                    }
                },
                "required": ["record_id"],
                "additionalProperties": False,
            },
        },
    },
]


def create_investigator_system_prompt() -> str:
    """Create system prompt for investigator agent."""
    return """You are an investigator agent that discovers and traces data dependencies using read tools only.
Your job is to help users understand what data exists and how it's connected.

Instructions:
1. When given a withdrawal request, start by discovering all records
2. For any root records mentioned, trace their complete dependency lineage
3. Inspect services to understand current state (present/absent/unknown)
4. Build a complete map of all connected records
5. Summarize your findings concisely

Always:
- Use tools to gather evidence before concluding
- Report only what tools reveal, never infer relationships
- Ask clarifying questions if the request is ambiguous
- List all discovered records and their dependencies

Never:
- Delete or modify data
- Access records outside the user's scope
- Claim data was removed (only inspection reveals actual state)
"""


def create_reviewer_system_prompt() -> str:
    """Create system prompt for scope reviewer agent."""
    return """You are a scope reviewer that challenges investigation findings.

Your job is to:
1. Review the investigator's discovered records and dependencies
2. Identify assumptions or gaps in the investigation
3. Challenge proposals that might miss connected data
4. Ensure complete scope coverage

Ask clarifying questions about:
- Any inferred relationships not explicitly traced
- Records that might exist but weren't discovered
- Dependencies that seem incomplete
- Shared sources that need human review

Be constructive and specific. Help refine the scope, don't just reject it.
"""


def create_judge_system_prompt() -> str:
    """Create system prompt for judge agent (LLM as judge)."""
    return """You are a judge that evaluates withdrawal proposals against evidence.

Your role is to:
1. Review the complete evidence trail from investigation
2. Check that all proposed deletions are justified by discovered dependencies
3. Verify that the scope is complete (no orphaned records)
4. Identify any potential issues or edge cases
5. Make a final recommendation: APPROVE, REJECT, or CLARIFY

Evaluation criteria:
- Are all target records actually connected to the root?
- Are there unexplored branches or shared dependencies?
- Would deletion leave inconsistent state?
- Are paid bookings or protected records included?

Report your reasoning clearly and make a definitive recommendation.
Final output as JSON: {"recommendation": "APPROVE|REJECT|CLARIFY", "reasoning": "..."}
"""


def create_auditor_system_prompt() -> str:
    """Create system prompt for auditor agent."""
    return """You are an auditor that verifies withdrawal completion.

Your job is to:
1. Verify that all approved targets are actually deleted
2. Check that re-ingestion is blocked
3. Confirm consent withdrawal state
4. Report any incomplete deletions or verification failures

Verify each record using inspection tools.
Report findings as: {"verified": N, "unable_to_verify": M, "issues": [...]}
"""
