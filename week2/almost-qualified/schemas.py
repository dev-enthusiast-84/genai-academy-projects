from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


STATUSES = {"Supported", "Partially supported", "No evidence found"}


@dataclass(frozen=True)
class Evidence:
    chunk_id: str
    source_id: str
    source_title: str
    excerpt: str
    score: float = 0.0


@dataclass
class AssessmentRow:
    requirement_id: str
    requirement_text: str
    requirement_citation: str
    status: str
    explanation: str
    evidence: list[Evidence] = field(default_factory=list)
    conflict_flag: bool = False
    missing_evidence: str = ""
    suggested_next_step: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AssessmentRow":
        evidence = [
            Evidence(
                chunk_id=str(item.get("chunk_id", "")),
                source_id=str(item.get("source_id", "")),
                source_title=str(item.get("source_title", "")),
                excerpt=str(item.get("excerpt", "")),
                score=float(item.get("score", 0.0) or 0.0),
            )
            for item in data.get("evidence", [])
            if isinstance(item, dict)
        ]
        return cls(
            requirement_id=str(data.get("requirement_id", "")),
            requirement_text=str(data.get("requirement_text", "")),
            requirement_citation=str(data.get("requirement_citation", "")),
            status=str(data.get("status", "")),
            explanation=str(data.get("explanation", "")),
            evidence=evidence,
            conflict_flag=bool(data.get("conflict_flag", False)),
            missing_evidence=str(data.get("missing_evidence", "")),
            suggested_next_step=str(data.get("suggested_next_step", "")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "requirement_text": self.requirement_text,
            "requirement_citation": self.requirement_citation,
            "status": self.status,
            "explanation": self.explanation,
            "evidence": [item.__dict__ for item in self.evidence],
            "conflict_flag": self.conflict_flag,
            "missing_evidence": self.missing_evidence,
            "suggested_next_step": self.suggested_next_step,
        }


def validate_assessment(row: AssessmentRow, chunks_by_id: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if row.status not in STATUSES:
        errors.append(f"{row.requirement_id}: invalid status {row.status!r}")
    if row.status == "No evidence found" and row.evidence:
        errors.append(f"{row.requirement_id}: unsupported row should not cite evidence")

    for item in row.evidence:
        chunk = chunks_by_id.get(item.chunk_id)
        if chunk is None:
            errors.append(f"{row.requirement_id}: unknown chunk {item.chunk_id}")
            continue
        if getattr(chunk, "category", "") != "candidate":
            errors.append(f"{row.requirement_id}: cited non-candidate chunk {item.chunk_id}")
        if item.excerpt and item.excerpt not in getattr(chunk, "text", ""):
            errors.append(f"{row.requirement_id}: excerpt is not present in {item.chunk_id}")
    return errors
