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
- Lets the user select a model/provider through LiteLLM: OpenAI, Google Gemini, Anthropic Claude, or Groq.
- Runs without an API key using deterministic local assessment, so retrieval and UI can be tested immediately.

## Retrieval

The submitted MVP uses local BM25 retrieval over the demo corpus so it can run immediately on a laptop or Streamlit Community Cloud. Pinecone is still a good next step for the larger private version, but it is not required for the two-hour demo build.

## Run Locally

Requires `uv` for Python dependency management. [Install uv](https://docs.astral.sh/uv/getting-started/) if you don't have it.

From the repository root:

```bash
cd week2/almost-qualified
uv sync
uv run python ingest.py --corpus demo
uv run streamlit run app.py
```

### Configure API Keys

Copy the secrets template and add your API keys:

```bash
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` with your credentials:

```toml
# OpenAI - https://platform.openai.com/api-keys
OPENAI_API_KEY = "sk-..."

# Google Gemini - https://ai.google.dev/
GOOGLE_API_KEY = "..."

# Anthropic Claude - https://console.anthropic.com/
ANTHROPIC_API_KEY = "sk-ant-..."

# Groq - https://console.groq.com/
GROQ_API_KEY = "..."
```

The sidebar accepts temporary API keys too. They stay in the browser session and are not written to disk.

## Evaluation

Run:

```bash
python week2/almost-qualified/evaluate.py --corpus demo
```

The evaluation writes `submission_artifacts/evaluation_results.json`.

## Cloud Deployment

1. Push the repository to GitHub.
2. Deploy on Streamlit Community Cloud with entrypoint `week2/almost-qualified/app.py`.
3. Add API keys in Streamlit secrets (`OPENAI_API_KEY`, `GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`, or `GROQ_API_KEY`).
4. Keep `APP_MODE = "demo"` for the public version.
5. Test one supported case, one partial case, and one missing-evidence case before sharing.

The public demo runs without API keys if "Use model assessment" is disabled. Add API keys for LLM-backed assessment.

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
