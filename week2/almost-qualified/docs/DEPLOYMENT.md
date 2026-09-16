# Run and deploy Almost Qualified

[Overview](../README.md) · [Architecture](ARCHITECTURE.md) · [Pitch deck](pitch_deck.html)

## Local demo

Install [uv](https://docs.astral.sh/uv/getting-started/installation/). From the repository root:

```bash
cd week2/almost-qualified
uv sync --python 3.14
uv run python ingest.py --corpus demo
uv run streamlit run app.py
```

Use the URL printed by Streamlit. Turn **Use model assessment** off for a credential-free demo. Select a role and one to five requirements, then click **Assess evidence**.

The committed `uv.lock` requires Python 3.14 or newer. Use 3.14 for this setup. The app reads only the demo corpus; `APP_MODE` is not an implemented mode switch.

## Optional model credentials

From the app directory, copy the example only if you do not already have a secrets file:

```bash
cp -n .streamlit/secrets.example.toml .streamlit/secrets.toml
```

Add the key for your selected provider:

```toml
OPENAI_API_KEY = "your-openai-key"
# Or use the corresponding key for a configured alternative:
# GOOGLE_API_KEY = "your-google-key"
# ANTHROPIC_API_KEY = "your-anthropic-key"
```

Keep `.streamlit/secrets.toml` out of Git; it is ignored by the project. You can also enter a temporary key in the sidebar. Enable model assessment, select a model, and use **Check model** before assessing. The default is GPT-4 Turbo; the [architecture guide](ARCHITECTURE.md#agent-to-model-mapping) lists the configured alternatives.

## Streamlit Community Cloud

1. Push the app code, `pyproject.toml`, `uv.lock`, and demo documents to the GitHub branch you intend to deploy.
2. In Streamlit Community Cloud, create an app and select repository `dev-enthusiast-84/genai-academy-projects` and that branch.
3. Set the main file path to `week2/almost-qualified/app.py`.
4. In **Advanced settings**, select Python **3.14** to match this lockfile. If 3.14 is unavailable, resolve and test a compatible lockfile before deploying; do not use the current lockfile with Python 3.12.
5. For model mode, add the chosen provider key in the cloud Secrets field. Credentials are optional for local-rule assessment.
6. Deploy and inspect the build logs. Record the assigned app URL in the README and showcase after verifying it.

Community Cloud selects `uv.lock` before other dependency formats when it is present next to the app entrypoint. Select the interpreter in the deployment UI; `runtime.txt` alone is not a substitute for that setting. See the official [deployment instructions](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) and [dependency-file precedence](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies).

### Smoke checks

- In local mode, assess a Streamlit requirement and inspect the cited candidate document.
- Assess the AI Product Builder deployment requirement: expect partial support.
- Assess the Platform ML Engineer Kubernetes requirement: expect no evidence and no citations.
- Download the Markdown report and compare it with the visible assessment.
- If using an LLM, run Check model, then assess and review citations and validation notes. A successful readiness check alone does not verify structured assessment output.

### Troubleshooting

| Symptom | Check |
| --- | --- |
| Python or dependency resolution failure | Cloud Python version must match the current 3.14+ lockfile; entrypoint must point to the app folder |
| Missing key | Add the selected provider's key, or disable model assessment |
| Model not found / provider routing error | Verify access and the provider-compatible model ID in the sidebar; catalog entries are configuration, not availability guarantees |
| Related evidence missed | BM25 matches words; paraphrases can be missed |
| Model request fails | Inspect logs; provider exceptions are not universally caught by the current fallback |

## GitHub Pages showcase and deck

The existing repository site publishes from root `docs/`. The project-owned source page is `week2/almost-qualified/site/index.html`; the canonical pitch deck stays in `week2/almost-qualified/docs/pitch_deck.html`.

After editing either artifact, run from the repository root:

```bash
python3 week2/almost-qualified/scripts/sync_showcase.py
```

The script copies only the public showcase and deck to `docs/almost-qualified/`, and adjusts their local links for Pages. It does not copy app configuration or secrets. The speaker script and longer documentation link to their GitHub source pages.

Publish the updated root `docs/` files to the branch configured in **Settings → Pages**. For the repository's documented setup, choose **Deploy from a branch**, branch **main**, folder **/docs**. See [GitHub's publishing-source guide](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

Expected routes after publication:

- Project: `https://dev-enthusiast-84.github.io/genai-academy-projects/almost-qualified/`
- Deck: `https://dev-enthusiast-84.github.io/genai-academy-projects/almost-qualified/pitch_deck.html`

Open the deck and test arrow-key navigation and Print / save PDF. GitHub's file viewer shows HTML source; the Pages URL renders the presentation. GitHub Pages hosts the static documentation, while Streamlit hosts the running application.
