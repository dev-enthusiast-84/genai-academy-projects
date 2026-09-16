# Getting started

Recall runs a Streamlit dashboard and three local customer services. Live investigations connect to OpenAI or OpenRouter.

Use Python 3.10 or newer, a POSIX shell (macOS, Linux, or WSL), and Make. The minimum Python version follows [Streamlit 1.56's package requirements](https://pypi.org/project/streamlit/1.56.0/). Node.js with `node --test` support is needed for the browser-engine tests.

From the repository root:

```bash
cd week3
python3 -m venv .venv
source .venv/bin/activate
make install
# Create only if no local .env exists:
test -f .env || cp .env.example .env
```

For live investigation, edit `.env` locally to set `OPENAI_API_KEY`, or configure OpenRouter as described in [Configuration](configuration.md). Run `make doctor` to query the provider's model catalog and check the selected models. Skip this network check for **Guided rehearsal**, which requires no API key.

```bash
make demo
```

Keep this terminal open. Recall is at http://127.0.0.1:8501; Club Portal is on 8101, Class Booking on 8102, and Member Offers on 8103. Run `make open-all` from another terminal in `week3/` to open all four apps. Make automatically uses `week3/.venv/bin/python` when present.

In Club Portal, give consent and share interests. Delete the questionnaire to demonstrate that downstream copies remain. In Recall, prepare a withdrawal plan, review the exact targets, approve it, and inspect verification results. Your paid booking remains outside the withdrawal scope.

Live mode sends authorized synthetic evidence to your selected provider and may incur charges. Guided rehearsal performs local deletion and verification with a scripted investigation.

Ctrl+C or `make stop` stops managed demo processes. `make restart` preserves saved data. `make reset` resets synthetic data and request history. `make test` runs Python and browser-engine checks without live model calls.

See [Deployment](deployment.md) for GitHub Pages publishing, custom launcher options, and persistent storage; [Demo guide](demo-guide.md) and [Troubleshooting](troubleshooting.md) cover the workflow.
