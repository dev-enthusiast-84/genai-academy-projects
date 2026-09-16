# Recall — four-app fitness demo

[Start the scenario](https://dev-enthusiast-84.github.io/genai-academy-projects/recall/scenario.html) · [Open Recall](https://dev-enthusiast-84.github.io/genai-academy-projects/recall/)

Recall embeds Club Portal, Class Booking, and Member Offers on one page. Accept consent in the embedded Club Portal to watch the other apps personalize automatically, without refreshing or switching tabs. Source-only deletion leaves those copies; approved Recall withdrawal updates all three views and preserves the paid booking. Each customer app also remains available on its own page.

Run from the repository root:

```bash
python3 -m http.server 8502 --bind 127.0.0.1 --directory week3/site
node --test week3/tests/pages.test.mjs
# Optional browser regression (requires Python Playwright and Chromium):
python3 week3/tests/embedded_apps.py
```

Use an OpenRouter key or HTTPS/CORS-enabled LiteLLM proxy for live investigation. Keys stay in memory. The labeled sample workflow is scripted; local removal, recovery, and verification are functional. All service data is synthetic and browser-local.

[Framework](../docs/PAGES_FRAMEWORK.md) · [Presenter notes](../docs/PAGES_DEMO.md)
