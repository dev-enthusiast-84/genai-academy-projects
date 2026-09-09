from __future__ import annotations

import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_DIR))

from agent import EvidenceAgent
from rag import build_manifest, extract_requirements, load_chunks, load_jobs


def test_job_requirements_are_not_candidate_evidence() -> None:
    build_manifest()
    chunks = load_chunks()
    jobs = load_jobs()
    job = jobs["Job description: Platform ML Engineer"]
    requirement = next(item for item in extract_requirements(job) if "Kubernetes" in item["text"])
    rows, errors = EvidenceAgent(chunks).assess([requirement], use_model=False)
    assert not errors
    assert rows[0].status == "No evidence found"
    assert rows[0].evidence == []


def test_deployment_instructions_are_partial_evidence() -> None:
    build_manifest()
    chunks = load_chunks()
    jobs = load_jobs()
    job = jobs["Job description: AI Product Builder Intern"]
    requirement = next(item for item in extract_requirements(job) if "Deploy prototypes" in item["text"])
    rows, errors = EvidenceAgent(chunks).assess([requirement], use_model=False)
    assert not errors
    assert rows[0].status == "Partially supported"
    assert rows[0].evidence
