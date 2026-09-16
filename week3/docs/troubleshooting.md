# Troubleshooting

## Provider connection

Recall supports OpenAI and OpenRouter. Set `LLM_PROVIDER=openai` or `LLM_PROVIDER=openrouter` in `.env`. Use `OPENAI_API_KEY` for OpenAI and `OPENROUTER_API_KEY` for OpenRouter. Keep credentials private.

Run `make doctor` to check connectivity and model selections. In the sidebar, **Load available models** retrieves the provider catalog. Select a tool-capable model for every role; the judge must differ from the investigator. If access fails, check your account permissions, quota, endpoint, and internet connection.

Use **Guided rehearsal** to exercise the workflow without live model calls.

## Demo does not start

Install dependencies with `make install`. The dashboard uses port 8501; customer services use ports 8101–8103. Stop an older manually launched demo in its terminal before running `make demo`. Use `make logs` to inspect managed processes and their launch terminal for output.

`make restart` restarts managed apps while preserving data. `make stop` only stops processes tracked by this project's launcher.

## Approval unavailable

The proposal must pass review before approval. Resolve clarification requests, ensure the judge differs from the investigator, and prepare a new plan when required. Tick the deletion and re-ingestion approval checkbox before approving. Preparation itself does not delete records.

## Partial withdrawal

Inspect the receipt and execution timeline. Restore unavailable customer services and use **Restore demo services & resume**. Completed work remains saved. Exhausted retries or a changed scope require a new investigation and approval.

## Reset or inspect

Download the verification receipt for the current request. `make reset` clears synthetic data and request history. Do not reset if you need to preserve evidence of the current run.

See [Configuration](configuration.md) and [Demo guide](demo-guide.md).

## GitHub Pages is missing updates or assets

Run `python3 scripts/pages_artifacts.py --check` from `week3/`. Pages serves the repository’s `docs/recall/` copy, so source changes in `site/` must be synchronized, committed, and pushed. See [Deployment](deployment.md) for the publishing folder, preview command, and deployment checks.
