from __future__ import annotations

import argparse
import json

from rag import MANIFEST_PATH, build_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the local demo corpus manifest.")
    parser.add_argument("--corpus", default="demo", choices=["demo"], help="Corpus to ingest.")
    args = parser.parse_args()
    manifest = build_manifest()
    print(json.dumps({"corpus": args.corpus, "manifest": str(MANIFEST_PATH), "corpus_version": manifest["corpus_version"], "chunks": len(manifest["chunks"])}, indent=2))


if __name__ == "__main__":
    main()
