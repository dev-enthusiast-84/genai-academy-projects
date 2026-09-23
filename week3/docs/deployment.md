# Deployment and drift

## Local primary app

`make demo` starts three standard-library HTTP customer services on loopback ports 8101–8103 and Streamlit on 8501. The launcher owns its children, preserves state unless `--reset` was explicitly passed, and cleans up those children on exit. Optional MCP adds port 8104. There is no model server, container cluster, SMTP server or cloud backend deployment in this project.

## Static public demo

Public URL: https://dev-enthusiast-84.github.io/genai-academy-projects/recall/

Canonical assets live in `week3/site/`. GitHub Pages serves a separate copy under the repository-level `docs/recall/`, with `.nojekyll` at the publishing root. The repository README describes Pages as `main` branch, `/docs` folder. This is a static JavaScript deployment; it does not run Python, SQLite service processes, the model reviewer/judge, or Slack notifications.

From `week3/`:

```bash
make pages-check  # nonzero if staged assets differ
make pages-sync   # copy only maintained public assets into ../docs/recall
make pages-check
```

The sync command does not commit, push, deploy, copy `.env`, or copy runtime files. Review the repository diff before committing/pushing the Pages branch. Local source edits and staged assets do not change the live URL until publication completes. If using a different publishing location, pass `--destination PATH` to `scripts/pages_artifacts.py`.

For local browser testing: `python3 -m http.server 8502 --bind 127.0.0.1 --directory site`. Use a separate browser profile/context for audit tests so its synthetic data cannot overwrite an existing demonstration.

## Verify publication

Staged files do not prove publication. Check the deployed routes and compare assets after publishing. The [archived public observation](audit/public-observation.json) is dated evidence, not a current availability guarantee. See [evaluation](EVALUATION.md) for evidence boundaries.
