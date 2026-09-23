# Recall — consent has an undo button

Recall helps fitness-club members withdraw personalization consent and remove linked questionnaire copies through a privacy dashboard, replacing manual requests and removal checks across three apps; it autonomously investigates with three read tools, coordinates reviewed and human-approved removal and verification, hands off when intent or evidence is unclear and before deletion, and targets verified removal with the paid booking preserved in under three minutes in at least 9 of 10 completable controlled live trials.

**The 9/10 and three-minute figures are targets, not measured performance.** This is a synthetic, single-user demonstration of an agentic workflow with human-approved writes.

## Run the primary implementation

From `week3/`, using Python 3.11+ (the audit environment uses Python 3.14):

```bash
python3 -m venv .venv
make install
# For a new setup only: copy .env.example to .env and add your provider key.
make doctor
make demo
```

OpenAI is the default; OpenRouter is also supported. Live investigations send the request and authorized synthetic metadata to your selected provider and may incur charges. **Guided rehearsal** uses scripted investigation without model calls.

| App | Address | User action |
| --- | --- | --- |
| Recall | http://127.0.0.1:8501 | Investigate, review, approve, verify |
| Club Portal | http://127.0.0.1:8101 | Give consent or delete only the source questionnaire |
| Class Booking | http://127.0.0.1:8102 | Inspect recommendations and the protected paid booking |
| Member Offers | http://127.0.0.1:8103 | Inspect the queued invitation preview; nothing is sent |

## Demonstrate the workflow

1. Give consent in Club Portal and inspect personalization in the other apps.
2. Delete only the questionnaire; its downstream copies remain.
3. Prepare a withdrawal plan in Recall. Review readable record/app names and the findings.
4. Tick approval, withdraw, and verify removal, blocked reuse, and the preserved booking.
5. Try an offline service or worker interruption, then restore and resume. Reset only to start a new consent journey.

## Commands

| Command | Action |
| --- | --- |
| `make demo` / `make restart` | Start / restart managed apps; preserve saved state |
| `make stop` / `make logs` | Stop tracked processes / show their status |
| `make open-all` | Open the four apps |
| `make doctor` / `make demo-models` | Check provider access / show model IDs without keys |
| `make test` | Python and browser-engine checks; no live model calls |
| `make test-browser` | Real browser workflow check; install `requirements-browser.txt` and Chromium first |
| `make pages-check` / `make pages-sync` | Compare / stage the static public app in the repository's `docs/recall` folder |
| `make reset` | Clear synthetic data and history and start a fresh demo |
| `make clean` | Clear Python/test caches; preserve saved data |

See [configuration](docs/configuration.md) for optional MCP and Slack. There is no local model server or model-download infrastructure.

## Hosted browser demo

[Open the public demo](https://dev-enthusiast-84.github.io/genai-academy-projects/recall/) · [Source](site/README.md) · [Deployment](docs/deployment.md)

The hosted demo is a static JavaScript app with simulated browser-local stores and one live investigator. It does not run the local multi-role Python pipeline or separate service databases. Publishing requires staging the assets, reviewing the diff, and pushing the Pages branch; local edits alone do not update the public URL.

## Project evidence

- [Handout questionnaire and one-liner](docs/FRAMEWORK.md)
- [Architecture](docs/architecture.md) and [API](docs/api.md)
- [Evaluation and limitations](docs/EVALUATION.md)
- [Submission document draft](docs/SUBMISSION.md) and [three-minute demo script](docs/demo-script-3-min.md)

The Google Doc, recorded video, and final submission are separate deliverables; their status is recorded in the submission draft.

The local agent workflow uses LangGraph for review/repair and approved execution. SQLite retains authoritative approval and recovery state; the hosted browser demo remains separate. See [architecture](docs/architecture.md).

[Documentation index](docs/index.md) · [Pitch deck and speaker script](docs/pitch/speaker-script.md) · [Contributing](CONTRIBUTING.md)
