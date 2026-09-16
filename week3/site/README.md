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

GitHub Pages serves the top-level repository folder `docs/recall/`. After editing `site/`, run `python3 scripts/pages_artifacts.py` and `python3 scripts/pages_artifacts.py --check`, then review and commit the synchronized artifacts. See [Deployment](../docs/deployment.md) for preview commands, publishing settings, and verification.

Use an OpenRouter or OpenAI key for live investigation. Keys stay in memory. The labeled sample workflow is scripted; local removal, recovery, and verification are functional. All service data is synthetic and browser-local.

[Framework](../docs/PAGES_FRAMEWORK.md) · [Presenter notes](../docs/PAGES_DEMO.md)
