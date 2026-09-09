from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
DEMO_DIR = PROJECT_DIR / "data" / "demo"
MANIFEST_PATH = PROJECT_DIR / "data" / "demo_manifest.json"


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    source_id: str
    source_title: str
    category: str
    section: str
    line_start: int
    line_end: int
    text: str
    content_hash: str


def normalize_source_id(path: Path) -> str:
    return path.stem.lower().replace(" ", "_").replace("-", "_")


def read_demo_documents(data_dir: Path = DEMO_DIR) -> list[dict[str, str]]:
    docs: list[dict[str, str]] = []
    for path in sorted(data_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        category = "job" if path.name.startswith("job_") else "candidate"
        title = next((line[2:].strip() for line in text.splitlines() if line.startswith("# ")), path.stem)
        docs.append(
            {
                "source_id": normalize_source_id(path),
                "source_title": title,
                "category": category,
                "text": text,
                "path": str(path),
            }
        )
    return docs


def chunk_documents(documents: list[dict[str, str]]) -> list[Chunk]:
    chunks: list[Chunk] = []
    for doc in documents:
        lines = doc["text"].splitlines()
        section = doc["source_title"]
        buffer: list[str] = []
        start_line = 1
        chunk_number = 1

        def flush(end_line: int) -> None:
            nonlocal buffer, start_line, chunk_number
            text = "\n".join(line for line in buffer if line.strip()).strip()
            if not text:
                buffer = []
                return
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
            chunks.append(
                Chunk(
                    chunk_id=f"{doc['source_id']}:{chunk_number:03d}",
                    source_id=doc["source_id"],
                    source_title=doc["source_title"],
                    category=doc["category"],
                    section=section,
                    line_start=start_line,
                    line_end=end_line,
                    text=text,
                    content_hash=digest,
                )
            )
            chunk_number += 1
            buffer = []

        for index, raw_line in enumerate(lines, start=1):
            line = raw_line.rstrip()
            if line.startswith("## "):
                flush(index - 1)
                section = line[3:].strip()
                start_line = index
                buffer = [line]
                continue
            if not buffer:
                start_line = index
            buffer.append(line)
            if len(tokenize("\n".join(buffer))) >= 130:
                flush(index)
                start_line = index + 1
        flush(len(lines))
    return chunks


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9][a-z0-9+#.-]*", text.lower())


class LocalRetriever:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self.candidate_chunks = [chunk for chunk in chunks if chunk.category == "candidate"]
        self.doc_freq: Counter[str] = Counter()
        self.term_freqs: dict[str, Counter[str]] = {}
        for chunk in self.candidate_chunks:
            terms = tokenize(chunk.text)
            counts = Counter(terms)
            self.term_freqs[chunk.chunk_id] = counts
            self.doc_freq.update(counts.keys())
        self.avgdl = sum(sum(counts.values()) for counts in self.term_freqs.values()) / max(len(self.term_freqs), 1)

    def search_candidate_evidence(self, query: str, top_k: int = 5) -> list[tuple[Chunk, float]]:
        query_terms = tokenize(query)
        scores: list[tuple[Chunk, float]] = []
        for chunk in self.candidate_chunks:
            score = self._bm25(query_terms, chunk)
            if score > 0:
                scores.append((chunk, score))
        scores.sort(key=lambda item: item[1], reverse=True)
        return scores[:top_k]

    def _bm25(self, query_terms: list[str], chunk: Chunk) -> float:
        counts = self.term_freqs[chunk.chunk_id]
        doc_len = sum(counts.values()) or 1
        total_docs = max(len(self.candidate_chunks), 1)
        score = 0.0
        k1 = 1.5
        b = 0.75
        for term in query_terms:
            tf = counts[term]
            if not tf:
                continue
            idf = math.log(1 + (total_docs - self.doc_freq[term] + 0.5) / (self.doc_freq[term] + 0.5))
            denom = tf + k1 * (1 - b + b * doc_len / max(self.avgdl, 1))
            score += idf * (tf * (k1 + 1)) / denom
        return score


def build_manifest(path: Path = MANIFEST_PATH) -> dict[str, object]:
    documents = read_demo_documents()
    chunks = chunk_documents(documents)
    version_seed = "|".join(chunk.content_hash for chunk in chunks)
    manifest = {
        "corpus_version": hashlib.sha256(version_seed.encode("utf-8")).hexdigest()[:12],
        "documents": [{key: value for key, value in doc.items() if key != "text"} for doc in documents],
        "chunks": [asdict(chunk) for chunk in chunks],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def load_chunks() -> list[Chunk]:
    if not MANIFEST_PATH.exists():
        build_manifest()
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return [Chunk(**item) for item in data["chunks"]]


def load_jobs() -> dict[str, str]:
    jobs: dict[str, str] = {}
    for doc in read_demo_documents():
        if doc["category"] == "job":
            jobs[doc["source_title"]] = doc["text"]
    return jobs


def extract_requirements(job_text: str) -> list[dict[str, str]]:
    requirements: list[dict[str, str]] = []
    in_requirements = False
    for line_number, raw_line in enumerate(job_text.splitlines(), start=1):
        line = raw_line.strip()
        if line.lower().startswith("## requirements"):
            in_requirements = True
            continue
        if in_requirements and line.startswith("## "):
            break
        if in_requirements and line.startswith("- "):
            requirement_id = f"REQ-{len(requirements) + 1:02d}"
            requirements.append(
                {
                    "requirement_id": requirement_id,
                    "text": line[2:].strip(),
                    "citation": f"job:{line_number}",
                }
            )
    return requirements


def chunks_by_id(chunks: list[Chunk]) -> dict[str, Chunk]:
    return {chunk.chunk_id: chunk for chunk in chunks}


def grouped_search(requirements: list[dict[str, str]], retriever: LocalRetriever, top_k: int = 5) -> dict[str, list[tuple[Chunk, float]]]:
    return {
        requirement["requirement_id"]: retriever.search_candidate_evidence(requirement["text"], top_k=top_k)
        for requirement in requirements
    }
