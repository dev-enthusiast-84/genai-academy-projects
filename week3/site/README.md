# Recall — four-app fitness demo

[Start the scenario](https://dev-enthusiast-84.github.io/genai-academy-projects/recall/scenario.html) · [Open Recall](https://dev-enthusiast-84.github.io/genai-academy-projects/recall/)

Club Portal, Class Booking, Member Offers, and Recall each have their own page. Consent in Club Portal automatically creates personalization in the other two apps. Source-only deletion leaves those copies; approved Recall withdrawal removes them and preserves the paid booking.

Run from the repository root:

```bash
python3 -m http.server 8502 --bind 127.0.0.1 --directory week3/site
node --test week3/tests/pages.test.mjs
```

Use an OpenRouter key or HTTPS/CORS-enabled LiteLLM proxy for live investigation. Keys stay in memory. The labeled sample workflow is scripted; local removal, recovery, and verification are functional. All service data is synthetic and browser-local.

[Framework](../docs/PAGES_FRAMEWORK.md) · [Presenter notes](../docs/PAGES_DEMO.md)
