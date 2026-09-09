"""Agent implementations following TECHNICAL-ARCHITECTURE.md: ADR-2 LLM routing

Per-Agent Models:
- Strategist:  Kimi 3 primary → Claude fallback
- Creator:     Claude 3.5 primary → Kimi 3 fallback
- Reviewer:    Kimi 3 primary → Claude fallback
"""

from .strategist import strategist_agent
from .creator import creator_agent
from .reviewer import reviewer_agent

__all__ = ["strategist_agent", "creator_agent", "reviewer_agent"]
