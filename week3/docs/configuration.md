# Configuration

Use `.env.example` as the starting point for a new `.env`; preserve existing keys when updating an established setup. Environment variables override nonempty file settings. Never commit `.env`.

## Providers

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key
OPENAI_INVESTIGATOR_MODEL=gpt-4.1-mini
OPENAI_SCOPE_REVIEWER_MODEL=gpt-4.1-mini
OPENAI_JUDGE_MODEL=gpt-4.1
OPENAI_AUDITOR_MODEL=gpt-4.1-mini
```

OpenAI uses its direct endpoint. For OpenRouter:

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your-key
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_INVESTIGATOR_MODEL=openai/gpt-5.4-mini
LLM_SCOPE_REVIEWER_MODEL=anthropic/claude-sonnet-4.6
LLM_JUDGE_MODEL=anthropic/claude-sonnet-4.6
LLM_AUDITOR_MODEL=anthropic/claude-sonnet-4.6
```

Model IDs are configurable examples, not availability or quality guarantees. Use **Load available models** or `make doctor` to check your account. The judge must have a different model ID from the investigator. Optional `LLM_MODEL` supplies legacy OpenRouter role defaults and `LLM_API_KEY` overrides its key; prefer the explicit settings above. Neither unsupported local providers nor a model proxy are started by the project.

## Runtime

`make demo` uses `.runtime/fitness/recall` for workflow state and `.runtime/fitness/applications` for three independent service stores. `run_demo.py --directory PATH` chooses another root; `--dashboard-port PORT` changes the dashboard port. Customer service ports 8101–8103 are defined in `withdrawal/services.py`.

The launcher generates `RECALL_SERVICE_TOKEN` and passes `RECALL_SERVICE_URLS`, `RECALL_DATA_DIR`, and `RECALL_DASHBOARD_URL` to its children. Do not manually expose these local services to the public internet.

## Optional MCP

```bash
make install-mcp
```

Set `RECALL_TOOL_TRANSPORT=mcp` in `.env` before `make demo`, or run `run_demo.py --mcp`. Default port 8104 can be changed with `RECALL_MCP_PORT`; `RECALL_MCP_URL` selects the loopback streamable HTTP URL. Default transport `http` requires no MCP dependency.

## Optional Slack status notifications

```env
NOTIFICATION_ENABLED=true
NOTIFICATION_PROVIDER=slack
NOTIFICATION_WEBHOOK_URL=https://hooks.slack.com/services/your/configured/destination
NOTIFICATION_EVENTS=awaiting_approval,review_blocked,partial,complete
NOTIFICATION_TIMEOUT_SECONDS=5
```

Also tick **Send status notifications to the configured Slack destination** in the dashboard sidebar. This explicitly enables external sends for the session; default configuration disables them. Only fixed status text and the request ID are sent, once per request/status; uncertain delivery is not automatically retried. No SMTP/email integration exists.

## Reset and re-consent

`make restart` preserves data. **Reset demo** or `make reset` clears synthetic history, consent and suppression for a fresh journey; then give consent in Club Portal again. Production re-consent with new identities/versions is outside this prototype.


## Troubleshooting and recovery

Open **Settings & reset** at the upper left of Recall for model settings and demo controls. A disabled plan button requires consent in Club Portal and a reload of Recall; live mode also requires configured models. Refresh the customer apps explicitly after consent or withdrawal.

- **Provider unavailable:** run `make doctor`, verify account access/quota, and use **Load available models** to check role selections. The judge must differ from the investigator. Guided rehearsal works without model calls.
- **Ports already occupied:** check the four app addresses before starting another instance. `make logs` reports only tracked processes. Stop a manually launched instance in its own terminal; `make stop` does not own it.
- **Approval unavailable:** resolve clarification/review findings, prepare a new plan when requested, and tick the exact deletion approval checkbox.
- **Reset:** tick **Reset all local synthetic data and request history**, then click **Reset demo**. A confirmation explains the cleared history/consent/blocks and restored starting data. Refresh all customer apps and give consent again. Download a receipt first if you need the previous run's evidence.

| Situation | Behavior and next step |
| --- | --- |
| Clarification or blocked review | No valid approval yet. Revise the request and prepare a new plan. |
| One temporary failure | At most two retries after the first delete attempt; inspect uncertain writes first. |
| App offline | Consent/suppression may already be recorded locally, but that app's deletion and blocks remain unverified. Show partial/unknown; restore the app and resume. |
| Worker interruption | Use the saved exact approval to resume remaining targets; do not repeat verified deletions. |
| Changed lineage or version | Existing approval cannot authorize the change; investigate and approve a new plan. |
| Expired approval or exhausted retries | Prepare a new plan and obtain fresh human approval. |
| Revoked further attempts | Stop future writes; already completed deletions remain irreversible. |
| Model auditor unavailable or unresolved | Keep the deterministic results visible without claiming a successful combined audit. |
| Completed withdrawal, want to test again | Reset the demo, then give consent again in Club Portal. |

The **Restore demo services & resume** button clears injected faults. A genuinely stopped service must be restarted (for example with `make restart`) before retrying. Reset is not needed to recover an unfinished approved withdrawal.
