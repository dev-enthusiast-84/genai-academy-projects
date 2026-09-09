# Almost Qualified

Almost Qualified is a Week 2 RAG app that helps career changers compare job requirements with evidence from their own resume and project notes.

Project statement:

> My RAG app helps career changers answer which job requirements their documented experience supports and what evidence is missing, from one resume, three project write-ups, and three saved job descriptions, in a Streamlit evidence workspace with a target of 95% faithfulness and 80% retrieval precision@5.

The demo corpus is fictional. It includes candidate documents, job descriptions, supported requirements, partial evidence, missing evidence, and explicit evidence boundaries.

## What It Does

- Lets the user choose a saved job description.
- Extracts the job requirements.
- Retrieves only candidate evidence for each requirement.
- Produces Supported, Partially supported, or No evidence found rows.
- Shows citation excerpts and source IDs.
- Lets the user download a Markdown assessment.
- Lets the user select a model/provider through LiteLLM, with OpenRouter as the recommended route.
- Runs without an API key using deterministic local assessment, so retrieval and UI can be tested immediately.

## Retrieval

The submitted MVP uses local BM25 retrieval over the demo corpus so it can run immediately on a laptop or Streamlit Community Cloud. Pinecone is still a good next step for the larger private version, but it is not required for the two-hour demo build.

## Run Locally

From the repository root:

```bash
python3 -m venv week2/almost-qualified/.venv
source week2/almost-qualified/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r week2/almost-qualified/requirements.txt
python week2/almost-qualified/ingest.py --corpus demo
python -m streamlit run week2/almost-qualified/app.py
```

To use an LLM-backed assessment, add secrets through environment variables or `.streamlit/secrets.toml`:

```toml
DEFAULT_LLM_PROVIDER = "openrouter"
DEFAULT_LLM_MODEL = "openrouter/openai/gpt-5-mini"
OPENROUTER_API_KEY = "replace-me"
```

The sidebar also accepts a temporary local API key. It stays in the browser session and is not written to disk.

## Evaluation

Run:

```bash
python week2/almost-qualified/evaluate.py --corpus demo
```

The evaluation writes `submission_artifacts/evaluation_results.json`.

## Cloud Deployment

1. Push the repository to GitHub.
2. Deploy on Streamlit Community Cloud with entrypoint `week2/almost-qualified/app.py`.
3. Add `OPENROUTER_API_KEY`, `DEFAULT_LLM_PROVIDER`, and `DEFAULT_LLM_MODEL` in Streamlit secrets.
4. Keep `APP_MODE = "demo"` for the public version.
5. Run one supported case, one partial case, and one missing-evidence case before sharing.

The public demo can run without a model key if "Use model assessment" is off. Add `OPENROUTER_API_KEY` for LLM-backed assessment.

## Files

```text
app.py
agent.py
model_config.py
rag.py
schemas.py
ingest.py
evaluate.py
data/demo/
evals/cases.json
tests/test_boundaries.py
```
