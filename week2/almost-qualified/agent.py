from __future__ import annotations

import json
import re

from model_config import ModelOption, litellm_completion
from rag import Chunk, LocalRetriever, chunks_by_id, grouped_search
from schemas import AssessmentRow, Evidence, validate_assessment


SUPPORTED_TERMS = {
    "streamlit",
    "python",
    "pandas",
    "altair",
    "pytest",
    "tests",
    "readme",
    "documentation",
    "structured",
    "validation",
    "limitations",
    "export",
    "workflow",
}

UNSUPPORTED_TERMS = {
    "kubernetes",
    "docker",
    "terraform",
    "soc2",
    "compliance",
    "ci/cd",
    "containerized",
    "monitor",
    "monitoring",
    "production",
}


class EvidenceAgent:
    def __init__(self, chunks: list[Chunk], model_option: ModelOption | None = None, api_key: str = ""):
        self.chunks = chunks
        self.chunk_map = chunks_by_id(chunks)
        self.retriever = LocalRetriever(chunks)
        self.model_option = model_option
        self.api_key = api_key

    def assess(self, requirements: list[dict[str, str]], use_model: bool = True) -> tuple[list[AssessmentRow], list[str]]:
        search_results = grouped_search(requirements, self.retriever, top_k=5)
        if use_model and self.model_option and self.api_key:
            rows, errors = self._model_assess(requirements, search_results)
            if rows and not errors:
                return rows, []
        rows = [self._heuristic_row(requirement, search_results[requirement["requirement_id"]]) for requirement in requirements]
        errors = [error for row in rows for error in validate_assessment(row, self.chunk_map)]
        return rows, errors

    def _model_assess(
        self,
        requirements: list[dict[str, str]],
        search_results: dict[str, list[tuple[Chunk, float]]],
    ) -> tuple[list[AssessmentRow], list[str]]:
        evidence_payload = {
            requirement["requirement_id"]: [
                {
                    "chunk_id": chunk.chunk_id,
                    "source_id": chunk.source_id,
                    "source_title": chunk.source_title,
                    "excerpt": best_excerpt(chunk.text, requirement["text"]),
                    "score": round(score, 3),
                }
                for chunk, score in search_results[requirement["requirement_id"]]
            ]
            for requirement in requirements
        }
        prompt = {
            "requirements": requirements,
            "candidate_evidence": evidence_payload,
            "allowed_statuses": ["Supported", "Partially supported", "No evidence found"],
            "rules": [
                "Use only candidate_evidence, never the job text, as proof of experience.",
                "Do not infer production deployment from deployment instructions.",
                "If evidence is weak or indirect, choose Partially supported.",
                "If no candidate evidence supports a requirement, choose No evidence found and cite no evidence.",
                "Return JSON only with key rows.",
            ],
        }
        content = litellm_completion(
            model=self.model_option.model_id,
            api_key=self.api_key,
            messages=[
                {"role": "system", "content": "You are a careful RAG evidence evaluator for job requirements."},
                {"role": "user", "content": json.dumps(prompt)},
            ],
            response_format={"type": "json_object"},
        )
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            return [], [f"Model returned invalid JSON: {exc}"]
        raw_rows = data.get("rows", [])
        rows = [AssessmentRow.from_dict(item) for item in raw_rows if isinstance(item, dict)]
        errors = [error for row in rows for error in validate_assessment(row, self.chunk_map)]
        if len(rows) != len(requirements):
            errors.append("Model returned the wrong number of assessment rows.")
        return rows, errors

    def _heuristic_row(self, requirement: dict[str, str], results: list[tuple[Chunk, float]]) -> AssessmentRow:
        text = requirement["text"]
        lower = text.lower()
        evidence = [
            Evidence(
                chunk_id=chunk.chunk_id,
                source_id=chunk.source_id,
                source_title=chunk.source_title,
                excerpt=best_excerpt(chunk.text, text),
                score=round(score, 3),
            )
            for chunk, score in results[:3]
            if score > 0
        ]

        tokens = {token.strip(".,;:!?") for token in re.findall(r"[a-z0-9+#./-]+", lower)}
        if tokens & UNSUPPORTED_TERMS:
            status = "No evidence found"
            evidence = []
            explanation = "The candidate corpus does not contain evidence for this specialized platform or production requirement."
            missing = "Add a concrete project note, deployment record, or work example that demonstrates this requirement."
        elif evidence and (tokens & SUPPORTED_TERMS):
            status = "Supported"
            explanation = "The candidate corpus contains direct evidence for the core tools or behaviors in this requirement."
            missing = ""
        elif evidence:
            status = "Partially supported"
            explanation = "The retrieved evidence is related, but it does not prove the full scope of the requirement."
            missing = "Clarify ownership, outcome, scale, or whether the work actually reached deployment."
        else:
            status = "No evidence found"
            explanation = "No supporting candidate evidence was retrieved from the current corpus."
            missing = "Add a resume bullet or project write-up with specific evidence."

        if "deploy" in lower and evidence:
            status = "Partially supported"
            explanation = "The corpus documents deployment instructions or familiarity, but not confirmed production operation."
            missing = "Add the deployed URL, date, owner contribution, and any usage or monitoring evidence."

        if "service" in lower and evidence:
            status = "Partially supported"
            explanation = "The corpus supports Python tests and documentation, but it does not prove service development or operation."
            missing = "Add a project note that names the service, interface, deployment context, and tests."

        return AssessmentRow(
            requirement_id=requirement["requirement_id"],
            requirement_text=text,
            requirement_citation=requirement["citation"],
            status=status,
            explanation=explanation,
            evidence=evidence,
            conflict_flag="does not claim" in " ".join(item.excerpt.lower() for item in evidence),
            missing_evidence=missing,
            suggested_next_step=suggest_next_step(status, text),
        )


def best_excerpt(text: str, query: str, max_chars: int = 340) -> str:
    segments = [line.strip() for line in text.splitlines() if line.strip()]
    sentences = segments or [text]
    query_terms = set(re.findall(r"[a-z0-9+#.-]+", query.lower()))
    best = max(sentences or [text], key=lambda sentence: len(query_terms & set(re.findall(r"[a-z0-9+#.-]+", sentence.lower()))))
    if len(best) <= max_chars:
        return best
    return best[: max_chars - 3].rstrip() + "..."


def suggest_next_step(status: str, requirement: str) -> str:
    if status == "Supported":
        return "Use the cited evidence as the interview talking point."
    if status == "Partially supported":
        return "Add one sentence that states ownership, outcome, and scope."
    return f"Add a project or resume bullet that directly demonstrates: {requirement}"


def render_markdown(rows: list[AssessmentRow]) -> str:
    lines = ["# Almost Qualified assessment", ""]
    for row in rows:
        lines.extend(
            [
                f"## {row.requirement_id}: {row.status}",
                "",
                f"Requirement: {row.requirement_text}",
                "",
                row.explanation,
                "",
            ]
        )
        if row.evidence:
            lines.append("Evidence:")
            for item in row.evidence:
                lines.append(f"- {item.source_title} `{item.chunk_id}`: {item.excerpt}")
            lines.append("")
        if row.missing_evidence:
            lines.extend([f"Missing evidence: {row.missing_evidence}", ""])
        lines.extend([f"Next step: {row.suggested_next_step}", ""])
    return "\n".join(lines).strip() + "\n"
