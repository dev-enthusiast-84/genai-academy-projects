from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

try:
    import streamlit as st
except Exception:  # pragma: no cover - streamlit is optional for CLI checks
    st = None


@dataclass(frozen=True)
class ModelOption:
    provider: str
    display_name: str
    model_id: str
    key_env: str
    note: str


MODEL_CATALOG = [
    ModelOption("openrouter", "OpenRouter: GPT-5 mini", "openrouter/openai/gpt-5-mini", "OPENROUTER_API_KEY", "Recommended if you have an OpenRouter key."),
    ModelOption("openrouter", "OpenRouter: Claude Sonnet", "openrouter/anthropic/claude-sonnet-4", "OPENROUTER_API_KEY", "Good reasoning model if available in your account."),
    ModelOption("openrouter", "OpenRouter: Gemini Flash", "openrouter/google/gemini-2.5-flash", "OPENROUTER_API_KEY", "Fast option for demos."),
    ModelOption("openai", "OpenAI: GPT-5 mini", "openai/gpt-5-mini", "OPENAI_API_KEY", "Use if you have Platform API billing."),
    ModelOption("anthropic", "Anthropic: Claude Sonnet", "anthropic/claude-sonnet-4-5", "ANTHROPIC_API_KEY", "Use if you already have Anthropic API access."),
]


def get_secret(name: str) -> str:
    if st is not None:
        try:
            value = st.secrets.get(name)
            if value:
                return str(value)
        except Exception:
            pass
    return os.getenv(name, "")


def resolve_model(option_label: str | None = None, custom_model: str | None = None) -> ModelOption:
    option = next((item for item in MODEL_CATALOG if item.display_name == option_label), MODEL_CATALOG[0])
    if custom_model:
        return ModelOption(option.provider, f"Custom: {custom_model}", custom_model, option.key_env, option.note)
    return option


def get_api_key(option: ModelOption, temporary_key: str = "") -> tuple[str, str]:
    if temporary_key:
        return temporary_key, "temporary session key"
    value = get_secret(option.key_env)
    if value:
        return value, option.key_env
    return "", option.key_env


def litellm_completion(model: str, messages: list[dict[str, str]], api_key: str, response_format: dict[str, Any] | None = None) -> str:
    from litellm import completion

    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "api_key": api_key,
        "temperature": 0,
    }
    if response_format:
        kwargs["response_format"] = response_format
    response = completion(**kwargs)
    return response.choices[0].message.content or ""


def check_model_ready(option: ModelOption, api_key: str) -> tuple[bool, str]:
    if not api_key:
        return False, f"Missing {option.key_env}."
    try:
        content = litellm_completion(
            model=option.model_id,
            api_key=api_key,
            messages=[{"role": "user", "content": "Return the single word ready."}],
        )
    except Exception as exc:
        return False, f"Model check failed: {exc}"
    if "ready" not in content.lower():
        return False, f"Model responded, but not as expected: {content[:120]}"
    return True, "Model check passed."
