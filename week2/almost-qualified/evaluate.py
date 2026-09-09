from __future__ import annotations

import argparse
import json
from pathlib import Path

from agent import EvidenceAgent
from rag import PROJECT_DIR, extract_requirements, load_chunks, read_demo_documents


def find_requirement(requirements: list[dict[str, str]], contains: str) -> dict[str, str]:
    needle = contains.lower()
    for requirement in requirements:
        if needle in requirement["text"].lower():
            return requirement
    raise ValueError(f"No requirement contains {contains!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Almost Qualified demo cases.")
    parser.add_argument("--corpus", default="demo", choices=["demo"])
    args = parser.parse_args()

    cases_path = PROJECT_DIR / "evals" / "cases.json"
    cases = json.loads(cases_path.read_text(encoding="utf-8"))
    chunks = load_chunks()
    jobs = {doc["source_id"]: doc["text"] for doc in read_demo_documents() if doc["category"] == "job"}
    agent = EvidenceAgent(chunks)

    results = []
    for case in cases:
        job_id = case["job_file"].replace(".md", "")
        requirements = extract_requirements(jobs[job_id])
        requirement = find_requirement(requirements, case["requirement_contains"])
        rows, errors = agent.assess([requirement], use_model=False)
        row = rows[0]
        returned_sources = sorted({item.source_id for item in row.evidence})
        expected_sources = sorted(case["expected_source_ids"])
        status_ok = row.status == case["expected_status"]
        source_ok = all(source in returned_sources for source in expected_sources)
        if not expected_sources:
            source_ok = not returned_sources
        results.append(
            {
                "id": case["id"],
                "expected_status": case["expected_status"],
                "actual_status": row.status,
                "expected_source_ids": expected_sources,
                "actual_source_ids": returned_sources,
                "status_ok": status_ok,
                "source_ok": source_ok,
                "errors": errors,
            }
        )

    passed = sum(1 for item in results if item["status_ok"] and item["source_ok"] and not item["errors"])
    summary = {"corpus": args.corpus, "passed": passed, "total": len(results), "results": results}
    output_path = PROJECT_DIR / "submission_artifacts" / "evaluation_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
