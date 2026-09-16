# Recall — consent has an undo button

Withdraw fitness-personalization consent across Club Portal, Class Booking, and Member Offers. Recall investigates the data trail, asks for approval, removes the approved copies, and verifies the outcome while protecting the paid booking.

## Run locally

Recall connects directly to **OpenAI or OpenRouter**. Live investigations use your provider account and may incur API charges. Guided rehearsal works without a model connection.

Run from `week3/` with Python 3.10+ and Make. For a new setup:

```bash
python3 -m venv .venv
source .venv/bin/activate
test -f .env || cp .env.example .env
make install     # Install Python dependencies
# Edit .env for live mode; guided rehearsal needs no key.
make doctor      # Optional: check provider access for live mode
make demo        # Start the four apps
```

OpenAI is the default provider. It uses `gpt-4.1-mini` for investigation, scope review, and auditing, with `gpt-4.1` as the independent judge. Select OpenRouter in the sidebar to use its model catalog. The judge must differ from the investigator. Deterministic checks and human approval govern deletion.

See [getting started](docs/getting-started.md), [configuration](docs/configuration.md), and [deployment](docs/deployment.md) for setup and GitHub Pages publishing.

| App | Address |
|---|---|
| Recall | http://127.0.0.1:8501 |
| Club Portal | http://127.0.0.1:8101 |
| Class Booking | http://127.0.0.1:8102 |
| Member Offers | http://127.0.0.1:8103 |

## Commands

| Command | Action |
|---|---|
| `make restart` | Restart managed apps; preserve saved state |
| `make stop` | Stop only processes started by Make commands |
| `make logs` | Show managed processes; app output stays in its launch terminal |
| `make open-all` | Open the four apps |
| `make demo-models` | Show configured model IDs without credentials |
| `make test` | Run workflow and browser-engine tests, without model calls |
| `make reset` | Reset synthetic data and start a fresh demo |
| `make clean` | Clear caches; preserve runtime data |

If an older demo was started outside Make, stop it with Ctrl+C in its terminal before `make demo`.

## Demo flow

1. Give consent in Club Portal; see recommendations and offers appear in the other apps.
2. Delete the source profile. The downstream copies remain.
3. Ask Recall to investigate. Review the exact targets and approve withdrawal.
4. Verify that personalization disappears, the paid booking remains, and replay is blocked.

The current dashboard workflow view is preserved. Guided rehearsal uses a scripted investigation with real local deletion and verification; live mode uses the configured models.

See [framework](docs/FRAMEWORK.md) and [workflow recovery](docs/RECOVERY.md).
