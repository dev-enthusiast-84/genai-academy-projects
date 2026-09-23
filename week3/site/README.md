# Recall — four-app fitness demo

[Start the scenario](https://dev-enthusiast-84.github.io/genai-academy-projects/recall/scenario.html) · [Open Recall](https://dev-enthusiast-84.github.io/genai-academy-projects/recall/)

Recall embeds Club Portal, Class Booking, and Member Offers on one page. Accept consent in the embedded Club Portal to watch the other apps personalize automatically, without refreshing or switching tabs. Source-only deletion leaves those copies; approved Recall withdrawal updates all three views and preserves the paid booking. Each customer app also remains available on its own page.

Run from `week3/`:

```bash
python3 -m http.server 8502 --bind 127.0.0.1 --directory site
```

Open http://127.0.0.1:8502/. In another terminal, run `node --test tests/pages.test.mjs`.

For the optional browser regression, activate your Python virtual environment, then run:

```bash
python -m pip install playwright
python -m playwright install chromium
python tests/embedded_apps.py
```

GitHub Pages serves the top-level repository folder `docs/recall/`. After editing `site/`, run `make pages-sync` and `make pages-check`, then review and commit the synchronized artifacts. See [Deployment](../docs/deployment.md) for preview commands, publishing settings, and verification.

Use an OpenRouter or OpenAI key for live investigation. Keys stay in memory. The labeled sample workflow is scripted; local removal, recovery, and verification are functional. All service data is synthetic and browser-local.

## Demonstration

1. Open Recall's embedded customer apps (or `scenario.html`). Give consent in Club Portal.
2. Watch the recommendation and invitation preview appear automatically.
3. Delete only the questionnaire; the other apps retain their copies.
4. Connect a provider in Recall, investigate, review the targets, and approve withdrawal.
5. Confirm the recommendation and invitation disappear, the paid booking remains, and replay is blocked.

The sample/rehearsal path is scripted. For a recovery demonstration, select an offline service, inspect the partial result, then restore and resume. All customer records are simulated browser-local data. The browser model workflow has one investigator; it does not run LangGraph, the separate judge, or the outcome auditor.

Credentials stay in memory. Request state persists for 24 hours; provenance and withdrawal markers remain until reset. The same ownership, approval, protected-booking and unknown-state boundaries apply to this controlled simulation; they do not establish independent backend security.

See [local versus hosted capabilities](../docs/FRAMEWORK.md#local-versus-hosted) and [deployment](../docs/deployment.md). `make pages-check` detects drift; `make pages-sync` stages source assets without publishing.
