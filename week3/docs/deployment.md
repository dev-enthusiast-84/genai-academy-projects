# Deployment

Recall has two deployment paths: the connected Python demo and the static browser demo. Run the commands below from `week3/` unless otherwise indicated.

## Connected local app

Follow [Getting started](getting-started.md) to create `.venv`, install dependencies, and configure optional provider credentials. `make demo` starts Recall on 8501 and the customer services on 8101–8103. Keep the terminal open; Ctrl+C stops the apps. No model proxy is required.

The launcher binds to `127.0.0.1`. It is a local demo, and publishing `app.py` alone does not deploy its three customer services. GitHub Pages serves the browser version described below; it cannot run these Python processes.

Default saved state lives in `.runtime/fitness/recall/` and `.runtime/fitness/applications/`. `make restart` preserves it; `make reset` clears the synthetic workflow and starts again. For custom data or dashboard settings, activate `.venv` and run:

```bash
python run_demo.py --directory .runtime/my-demo --dashboard-port 8502
```

Stop this direct launch with Ctrl+C. `make stop` tracks only Make-managed launches. Customer ports remain 8101–8103, so two connected demos cannot share them. See [Configuration](configuration.md) for optional MCP setup.

## GitHub Pages browser app

The source is `week3/site/`. The repository publishes the top-level `docs/` directory, so Recall's public artifacts must be copied into `docs/recall/`. `week3/docs/` contains project documentation and is not the GitHub Pages publishing root.

Prepare and verify the public files:

```bash
python3 scripts/pages_artifacts.py
python3 scripts/pages_artifacts.py --check
node --test tests/pages.test.mjs
```

The script copies HTML, CSS, JavaScript modules, and synthetic JSON fixtures. It excludes `.env`, runtime databases, Python code, and development documentation. It does not delete destination files; review obsolete files separately when removing or renaming an asset. Relative asset paths support the `/genai-academy-projects/recall/` URL prefix.

Preview the actual publishing folder from `week3/`:

```bash
python3 -m http.server 8502 --bind 127.0.0.1 --directory ../docs
```

Open `http://127.0.0.1:8502/recall/`. Confirm that the three embedded apps load, consent updates recommendations, and the sample withdrawal preserves the paid booking. Keep all customer pages under the same origin so they share browser storage.

After reviewing the changes, commit the source and synchronized `docs/recall/` artifacts and push them to the publishing branch. In the GitHub repository, select **Settings → Pages → Deploy from a branch → main → /docs → Save**. These settings match the repository's documented publishing layout; verify the selected branch in GitHub. See [GitHub's publishing-source instructions](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

The expected published entry points are:

- [Recall](https://dev-enthusiast-84.github.io/genai-academy-projects/recall/)
- [Scenario overview](https://dev-enthusiast-84.github.io/genai-academy-projects/recall/scenario.html)
- [Club Portal](https://dev-enthusiast-84.github.io/genai-academy-projects/recall/club-portal.html)
- [Class Booking](https://dev-enthusiast-84.github.io/genai-academy-projects/recall/class-booking.html)
- [Member Offers](https://dev-enthusiast-84.github.io/genai-academy-projects/recall/member-offers.html)

Wait for the Pages deployment to succeed in GitHub Actions, then check those URLs and browser network requests for missing `.mjs`, `.css`, or `.json` files. If the hosted app is stale, run the artifact check, confirm the copied files were pushed to the publishing branch, and reload without cache.

The browser version uses synthetic records in local storage. Users enter their own model key for live investigation; keys stay in memory. The sample workflow needs no key. Browser state is separate from the local Python databases.
