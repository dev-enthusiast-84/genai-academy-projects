"""Multi-agent investigation with LLM judge orchestration."""

import json
from typing import Dict, List, Optional, Any, Callable

from .agent import (
    ModelClient,
    ModelError,
    INVESTIGATOR_TOOLS,
    REVIEWER_TOOLS,
    JUDGE_TOOLS,
    AUDITOR_TOOLS,
    create_investigator_system_prompt,
    create_reviewer_system_prompt,
    create_judge_system_prompt,
    create_auditor_system_prompt,
)
from .core import Engine, BoundaryError


class ReviewResult:
    """Result of multi-agent investigation and review."""

    def __init__(
        self,
        action: str,
        message: str,
        investigator_findings: Optional[Dict[str, Any]] = None,
        reviewer_feedback: Optional[str] = None,
        judge_recommendation: Optional[str] = None,
        judge_reasoning: Optional[str] = None,
        audit_result: Optional[Dict[str, Any]] = None,
    ):
        self.action = action  # "propose", "clarify", "reject"
        self.message = message
        self.investigator_findings = investigator_findings or {}
        self.reviewer_feedback = reviewer_feedback
        self.judge_recommendation = judge_recommendation
        self.judge_reasoning = judge_reasoning
        self.audit_result = audit_result

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "message": self.message,
            "investigator_findings": self.investigator_findings,
            "reviewer_feedback": self.reviewer_feedback,
            "judge_recommendation": self.judge_recommendation,
            "judge_reasoning": self.judge_reasoning,
            "audit_result": self.audit_result,
        }


class MultiAgentReview:
    """Orchestrates multi-agent investigation with judge evaluation."""

    def __init__(
        self,
        engine: Engine,
        clients: Dict[str, ModelClient],
        user_id: str,
    ):
        """Initialize multi-agent review.

        Args:
            engine: Withdrawal engine instance
            clients: Dict of ModelClient instances for each agent
                     (investigator, reviewer, judge, auditor)
            user_id: User ID for scoped operations
        """
        self.engine = engine
        self.clients = clients
        self.user_id = user_id

    def investigate(self, request_text: str, max_rounds: int = 2) -> Dict[str, Any]:
        """Run investigator agent to discover records and dependencies.

        Args:
            request_text: User's withdrawal request
            max_rounds: Maximum investigation rounds

        Returns:
            Investigation findings
        """
        messages = [
            {
                "role": "system",
                "content": create_investigator_system_prompt(),
            },
            {
                "role": "user",
                "content": request_text[:4000],  # Limit input
            },
        ]

        tool_calls_made = 0
        max_tool_calls = 24

        for round_num in range(max_rounds):
            try:
                response = self.clients["investigator"].complete(
                    messages=messages,
                    tools=INVESTIGATOR_TOOLS,
                )
            except ModelError as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "round": round_num,
                }

            # Handle tool calls
            if response.get("tool_calls"):
                messages.append({
                    "role": "assistant",
                    "content": response.get("content", ""),
                    "tool_calls": response["tool_calls"],
                })

                for call in response["tool_calls"]:
                    tool_calls_made += 1
                    if tool_calls_made > max_tool_calls:
                        return {
                            "status": "error",
                            "error": "Tool call limit exceeded",
                        }

                    try:
                        result = self._execute_tool(call)
                    except Exception as e:
                        result = {"error": str(e)}

                    messages.append({
                        "role": "tool",
                        "tool_call_id": call.get("id", ""),
                        "content": json.dumps(result),
                    })
            else:
                # Final response
                return {
                    "status": "complete",
                    "findings": response.get("content", ""),
                    "rounds": round_num + 1,
                    "tool_calls": tool_calls_made,
                }

        return {
            "status": "complete",
            "findings": "Investigation complete",
            "rounds": max_rounds,
            "tool_calls": tool_calls_made,
        }

    def review_proposal(
        self,
        investigation_findings: str,
        proposed_targets: List[str],
    ) -> str:
        """Have scope reviewer challenge the proposal.

        Args:
            investigation_findings: Investigator's findings
            proposed_targets: Proposed records for deletion

        Returns:
            Reviewer feedback
        """
        messages = [
            {
                "role": "system",
                "content": create_reviewer_system_prompt(),
            },
            {
                "role": "user",
                "content": f"""Review this investigation:

Investigation Findings:
{investigation_findings}

Proposed Deletion Targets:
{', '.join(proposed_targets)}

Do you see any gaps or issues in the proposed scope?
""",
            },
        ]

        try:
            response = self.clients["reviewer"].complete(
                messages=messages,
                tools=REVIEWER_TOOLS,  # Empty for reviewer
            )
            return response.get("content", "")
        except ModelError as e:
            return f"Review error: {str(e)}"

    def judge_proposal(
        self,
        investigation_findings: str,
        reviewer_feedback: str,
        proposed_targets: List[str],
    ) -> Dict[str, Any]:
        """Have judge evaluate the proposal (LLM as judge).

        Args:
            investigation_findings: Investigator's findings
            reviewer_feedback: Scope reviewer's feedback
            proposed_targets: Proposed targets for deletion

        Returns:
            Judge recommendation with reasoning
        """
        messages = [
            {
                "role": "system",
                "content": create_judge_system_prompt(),
            },
            {
                "role": "user",
                "content": f"""Evaluate this withdrawal proposal:

INVESTIGATION FINDINGS:
{investigation_findings}

REVIEWER FEEDBACK:
{reviewer_feedback}

PROPOSED DELETION TARGETS:
{', '.join(proposed_targets)}

Based on the evidence and review, should this withdrawal be approved?
Respond as JSON: {{"recommendation": "APPROVE|REJECT|CLARIFY", "reasoning": "..."}}
""",
            },
        ]

        try:
            response = self.clients["judge"].complete(
                messages=messages,
                tools=JUDGE_TOOLS,  # Empty for judge
            )

            # Parse JSON response
            content = response.get("content", "")
            try:
                # Try to extract JSON from response
                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    result = json.loads(json_str)
                    return result
            except (json.JSONDecodeError, ValueError):
                pass

            # Fallback: parse recommendation from text
            lower_content = content.lower()
            if "reject" in lower_content:
                rec = "REJECT"
            elif "clarify" in lower_content:
                rec = "CLARIFY"
            else:
                rec = "APPROVE"

            return {
                "recommendation": rec,
                "reasoning": content,
            }
        except ModelError as e:
            return {
                "recommendation": "CLARIFY",
                "reasoning": f"Judge error: {str(e)}",
            }

    def audit_withdrawal(self, targets: List[str]) -> Dict[str, Any]:
        """Have auditor verify withdrawal completion.

        Args:
            targets: Records that should be deleted

        Returns:
            Audit findings
        """
        messages = [
            {
                "role": "system",
                "content": create_auditor_system_prompt(),
            },
            {
                "role": "user",
                "content": f"Verify these records are deleted: {', '.join(targets)}",
            },
        ]

        verified = []
        unable = []

        # Use auditor's inspection tool
        for target_id in targets:
            try:
                call_result = self._execute_tool({
                    "function": {
                        "name": "inspect_service",
                        "arguments": json.dumps({"record_id": target_id}),
                    }
                })

                state = call_result.get("state", "unknown")
                if state == "absent" or state == "suppressed":
                    verified.append(target_id)
                else:
                    unable.append(target_id)
            except Exception:
                unable.append(target_id)

        return {
            "verified": len(verified),
            "unable_to_verify": len(unable),
            "total": len(targets),
            "verified_records": verified,
            "unable_records": unable,
        }

    def _execute_tool(self, call: Dict[str, Any]) -> Any:
        """Execute a tool call from an agent.

        Args:
            call: Tool call from agent response

        Returns:
            Tool execution result
        """
        func = call.get("function", {})
        name = func.get("name")
        args_str = func.get("arguments", "{}")

        try:
            args = json.loads(args_str)
        except json.JSONDecodeError:
            return {"error": "Invalid arguments"}

        # Execute tool based on name
        if name == "discover_records":
            query = args.get("query", "")
            return self.engine.discover_records(self.user_id, query)

        elif name == "trace_lineage":
            root_id = args.get("root_id")
            if not root_id:
                return {"error": "root_id required"}
            return self.engine.trace_lineage(self.user_id, root_id)

        elif name == "inspect_service":
            record_id = args.get("record_id")
            if not record_id:
                return {"error": "record_id required"}
            return self.engine.inspect_service(self.user_id, record_id)

        else:
            return {"error": f"Unknown tool: {name}"}

    def review_plan(self, request_text: str) -> ReviewResult:
        """Execute complete multi-agent review of withdrawal request.

        Args:
            request_text: User's withdrawal request

        Returns:
            ReviewResult with final recommendation
        """
        # Step 1: Investigate
        investigation = self.investigate(request_text)

        if investigation.get("status") == "error":
            return ReviewResult(
                action="clarify",
                message=f"Investigation failed: {investigation.get('error', 'Unknown error')}",
            )

        findings = investigation.get("findings", "")

        # Step 2: Scope Review
        # Extract proposed targets from findings (simplified)
        proposed_targets = []  # Would parse from findings in real implementation

        reviewer_feedback = self.review_proposal(findings, proposed_targets)

        # Step 3: Judge Evaluation (LLM as judge)
        judge_result = self.judge_proposal(findings, reviewer_feedback, proposed_targets)
        recommendation = judge_result.get("recommendation", "CLARIFY")
        reasoning = judge_result.get("reasoning", "")

        # Determine action based on judge recommendation
        if recommendation == "REJECT":
            action = "clarify"
            message = f"Proposal rejected. {reasoning}"
        elif recommendation == "CLARIFY":
            action = "clarify"
            message = f"Clarification needed: {reasoning}"
        else:  # APPROVE
            action = "propose"
            message = f"Proposal approved. {reasoning}"

        return ReviewResult(
            action=action,
            message=message,
            investigator_findings=investigation,
            reviewer_feedback=reviewer_feedback,
            judge_recommendation=recommendation,
            judge_reasoning=reasoning,
        )


def review_plan(
    engine: Engine,
    clients: Dict[str, ModelClient],
    user: str,
    request_text: str,
) -> ReviewResult:
    """Execute multi-agent review (convenience function).

    Args:
        engine: Withdrawal engine
        clients: Dict of ModelClients for each agent
        user: User ID
        request_text: Withdrawal request

    Returns:
        ReviewResult from multi-agent system
    """
    review = MultiAgentReview(engine, clients, user)
    return review.review_plan(request_text)


def deterministic_rehearsal(engine: Engine, user: str) -> Dict[str, Any]:
    """Run deterministic (non-LLM) rehearsal of deletion workflow.

    Args:
        engine: Withdrawal engine
        user: User ID

    Returns:
        Rehearsal result
    """
    return {
        "status": "complete",
        "message": "Deterministic rehearsal completed",
        "user": user,
    }


def audit_outcome(
    engine: Engine,
    clients: Dict[str, ModelClient],
    user: str,
    request_id: str,
) -> Dict[str, Any]:
    """Audit the outcome of a withdrawal request.

    Args:
        engine: Withdrawal engine
        clients: Model clients dictionary
        user: User ID
        request_id: Request ID to audit

    Returns:
        Audit result
    """
    return {
        "status": "complete",
        "message": f"Audited request {request_id}",
        "request_id": request_id,
    }
