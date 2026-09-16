"""LLM judge evaluation for withdrawal proposals."""

import json
from typing import Dict, List, Any, Optional
from enum import Enum

from .agent import ModelClient, ModelError, create_judge_system_prompt
from .core import Engine


class Recommendation(Enum):
    """Judge recommendation."""
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    CLARIFY = "CLARIFY"


class JudgeEvaluation:
    """Judge evaluation result."""

    def __init__(
        self,
        recommendation: Recommendation,
        reasoning: str,
        issues: Optional[List[str]] = None,
        suggestions: Optional[List[str]] = None,
    ):
        self.recommendation = recommendation
        self.reasoning = reasoning
        self.issues = issues or []
        self.suggestions = suggestions or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommendation": self.recommendation.value,
            "reasoning": self.reasoning,
            "issues": self.issues,
            "suggestions": self.suggestions,
        }


class JudgeAgent:
    """LLM judge for evaluating withdrawal proposals."""

    def __init__(self, client: ModelClient, engine: Engine, user_id: str):
        """Initialize judge agent.

        Args:
            client: ModelClient for judge
            engine: Withdrawal engine
            user_id: User ID
        """
        self.client = client
        self.engine = engine
        self.user_id = user_id

    def evaluate(
        self,
        investigation: str,
        review_feedback: str,
        proposed_targets: List[str],
        evidence_trail: Optional[List[Dict[str, Any]]] = None,
    ) -> JudgeEvaluation:
        """Evaluate a withdrawal proposal.

        Args:
            investigation: Investigator's findings
            review_feedback: Scope reviewer's feedback
            proposed_targets: Records proposed for deletion
            evidence_trail: Optional detailed evidence

        Returns:
            JudgeEvaluation with recommendation
        """
        # Build evaluation context
        context = self._build_context(
            investigation,
            review_feedback,
            proposed_targets,
            evidence_trail,
        )

        # Ask judge to evaluate
        try:
            response = self.client.complete(
                messages=[
                    {
                        "role": "system",
                        "content": create_judge_system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": context,
                    },
                ],
            )
        except ModelError as e:
            return JudgeEvaluation(
                recommendation=Recommendation.CLARIFY,
                reasoning=f"Judge error: {str(e)}",
                issues=["LLM service error"],
            )

        # Parse response
        return self._parse_response(response.get("content", ""))

    def _build_context(
        self,
        investigation: str,
        review_feedback: str,
        proposed_targets: List[str],
        evidence_trail: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Build evaluation context for judge.

        Args:
            investigation: Investigator findings
            review_feedback: Reviewer feedback
            proposed_targets: Proposed deletion targets
            evidence_trail: Optional evidence details

        Returns:
            Formatted context string
        """
        context = f"""WITHDRAWAL PROPOSAL EVALUATION

INVESTIGATION FINDINGS:
{investigation}

SCOPE REVIEWER FEEDBACK:
{review_feedback}

PROPOSED DELETION TARGETS ({len(proposed_targets)} records):
{json.dumps(proposed_targets, indent=2)}
"""

        if evidence_trail:
            context += f"\nEVIDENCE TRAIL:\n"
            for entry in evidence_trail:
                context += f"- {entry.get('type', 'unknown')}: {entry.get('description', '')}\n"

        context += """
EVALUATION CRITERIA:
1. Are all proposed targets justified by discovered evidence?
2. Are there unexplored branches or missing dependencies?
3. Would deletion create data inconsistencies?
4. Are protected records (paid bookings, public listings) included?
5. Is the scope complete and correct?

Make a definitive recommendation: APPROVE, REJECT, or CLARIFY.
Provide clear reasoning and any issues identified.

Output as JSON:
{
  "recommendation": "APPROVE|REJECT|CLARIFY",
  "reasoning": "Your detailed reasoning here",
  "issues": ["issue1", "issue2"],
  "suggestions": ["suggestion1", "suggestion2"]
}
"""
        return context

    def _parse_response(self, response: str) -> JudgeEvaluation:
        """Parse judge response.

        Args:
            response: Judge's response text

        Returns:
            JudgeEvaluation
        """
        # Try to extract JSON
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)

                rec_str = data.get("recommendation", "CLARIFY").upper()
                recommendation = Recommendation[rec_str] if rec_str in Recommendation.__members__ else Recommendation.CLARIFY

                return JudgeEvaluation(
                    recommendation=recommendation,
                    reasoning=data.get("reasoning", ""),
                    issues=data.get("issues", []),
                    suggestions=data.get("suggestions", []),
                )
        except (json.JSONDecodeError, KeyError, ValueError):
            pass

        # Fallback: parse from text
        lower_response = response.lower()

        if "reject" in lower_response:
            rec = Recommendation.REJECT
        elif "clarify" in lower_response or "question" in lower_response:
            rec = Recommendation.CLARIFY
        else:
            rec = Recommendation.APPROVE

        return JudgeEvaluation(
            recommendation=rec,
            reasoning=response,
        )

    def check_protected_records(self, proposed_targets: List[str]) -> Dict[str, Any]:
        """Check if protected records are in proposed targets.

        Args:
            proposed_targets: Records proposed for deletion

        Returns:
            Dict with protected records found
        """
        protected = {
            "paid_bookings": [],
            "public_listings": [],
        }

        for target_id in proposed_targets:
            try:
                record = self.engine.meta(target_id, self.user_id)
                kind = record.get("kind", "")

                if kind == "paid_booking":
                    protected["paid_bookings"].append(target_id)
                elif kind in {"public_listing", "class_listing"}:
                    protected["public_listings"].append(target_id)
            except Exception:
                pass

        return protected

    def check_scope_completeness(
        self,
        root_ids: List[str],
        proposed_targets: List[str],
    ) -> Dict[str, Any]:
        """Check if scope is complete for given roots.

        Args:
            root_ids: Root records for withdrawal
            proposed_targets: Proposed deletion targets

        Returns:
            Dict with completeness analysis
        """
        issues = []
        missing = []

        for root_id in root_ids:
            try:
                lineage = self.engine.trace_lineage(self.user_id, root_id)
                all_records = {r["id"] for r in lineage.get("records", [])}
                proposed_set = set(proposed_targets)

                missing_from_proposal = all_records - proposed_set
                if missing_from_proposal:
                    missing.extend(missing_from_proposal)
                    issues.append(
                        f"Root {root_id} has {len(missing_from_proposal)} "
                        f"dependent records not in proposal"
                    )
            except Exception as e:
                issues.append(f"Could not trace root {root_id}: {str(e)}")

        return {
            "issues": issues,
            "missing_records": missing,
            "complete": len(issues) == 0,
        }
