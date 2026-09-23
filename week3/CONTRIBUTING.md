# Contributing

Work from `week3/`. Create a virtual environment, run `make install`, and configure a provider only if exercising live mode. `make test` runs Python and JavaScript checks without model calls. For browser checks, install `requirements-browser.txt`, run `python -m playwright install chromium` using that environment, then `make test-browser`.

Keep approval, exact scope, version checks, preserved bookings and per-user boundaries enforced in application code. Use synthetic fixtures and temporary stores for tests; do not reset the running demo to test changes. Never commit credentials, runtime databases, receipts with sensitive content, or virtual environments.

Maintain `docs/FRAMEWORK.md`, `docs/api.md` and `docs/EVALUATION.md` when behavior changes. Keep local/hosted differences explicit. `make pages-check` detects drift and `make pages-sync` stages only the maintained static assets; review the repository diff before publishing.

Explain the user-visible change, relevant tests, and remaining limitations in a pull request. Do not claim a measured model success rate from deterministic or mocked tests.
