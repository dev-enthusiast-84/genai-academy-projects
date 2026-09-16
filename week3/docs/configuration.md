# Configuration Guide

Configure Recall for your needs.

## Environment Variables

Configuration is managed through the `.env` file. Copy `.env.example` to `.env` and customize:

```bash
test -f .env || cp .env.example .env
```

## Model providers

OpenAI is the default. Set credentials locally:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key
OPENAI_INVESTIGATOR_MODEL=gpt-4.1-mini
OPENAI_SCOPE_REVIEWER_MODEL=gpt-4.1-mini
OPENAI_JUDGE_MODEL=gpt-4.1
OPENAI_AUDITOR_MODEL=gpt-4.1-mini
```

For OpenRouter:

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your-key
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_INVESTIGATOR_MODEL=openai/gpt-5.4-mini
LLM_SCOPE_REVIEWER_MODEL=anthropic/claude-sonnet-4.6
LLM_JUDGE_MODEL=anthropic/claude-sonnet-4.6
LLM_AUDITOR_MODEL=anthropic/claude-sonnet-4.6
```

Use the sidebar to load available models. The judge must differ from the investigator. OpenAI settings use the `OPENAI_` prefix; OpenRouter role settings use `LLM_`. Run `make doctor` to check connectivity and model selections. Live requests send authorized synthetic evidence to your provider and may incur charges. Guided rehearsal requires no API key.

## Service Configuration

### Local Service Ports

```env
# Defined in withdrawal/services.py
# Club Portal: 8101
# Class Booking: 8102
# Member Offers: 8103
# Recall Dashboard: 8501
```

Set the dashboard port with `python run_demo.py --dashboard-port 8502` after activating `.venv`. Customer ports are defined in `withdrawal/services.py` (`PORTS`) and have no launcher override.

### Service URLs

The launcher generates `RECALL_SERVICE_URLS` for all three services and a fresh `RECALL_SERVICE_TOKEN`, shared by its child processes. It also sets `RECALL_DASHBOARD_URL`. Do not hardcode a token in `.env` for the standard launcher.

## Database Configuration

`make demo` stores Recall state in `.runtime/fitness/recall/` and service databases in `.runtime/fitness/applications/`. To change the parent directory, use:

```bash
python run_demo.py --directory /path/to/demo-data
```

The launcher sets `RECALL_DATA_DIR` to that directory's `recall/` subfolder, overriding any `.env` value. Standalone `app.py` defaults to `.runtime/fitness-local`, but does not start the connected services.

Use `make reset` to reset the managed demo's synthetic data and request history. For a custom directory, stop its launcher and run `python run_demo.py --directory /path/to/demo-data --reset`. Restarting without `--reset` preserves state.

## Notification Configuration

### Email Notifications

```env
NOTIFICATION_ENABLED=true
NOTIFICATION_PROVIDER=email
NOTIFICATION_SMTP_HOST=smtp.gmail.com
NOTIFICATION_SMTP_PORT=587
NOTIFICATION_SMTP_USERNAME=your-email@gmail.com
NOTIFICATION_SMTP_PASSWORD=app-password-here
NOTIFICATION_FROM_EMAIL=your-email@gmail.com
NOTIFICATION_TO_EMAIL=recipient@example.com
NOTIFICATION_EVENTS=awaiting_approval,review_blocked,partial,complete
NOTIFICATION_TIMEOUT_SECONDS=5
```

**For Gmail with 2FA:**

1. Enable 2-Step Verification
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Use the generated password (not your account password)

### Slack Notifications

```env
NOTIFICATION_ENABLED=true
NOTIFICATION_PROVIDER=slack
NOTIFICATION_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
NOTIFICATION_EVENTS=awaiting_approval,review_blocked,partial,complete
```

## Tool Transport Configuration

### HTTP Transport (Default)

```env
RECALL_TOOL_TRANSPORT=http
```

Agents communicate with services via HTTP API.

### MCP Transport (Advanced)

```env
RECALL_TOOL_TRANSPORT=mcp
RECALL_MCP_PORT=8104
RECALL_MCP_URL=http://127.0.0.1:8104/mcp
```

Install the optional SDK with `make install-mcp`, then restart using `make restart`. Alternatively, activate `.venv` and run `python run_demo.py --mcp`. HTTP transport does not require this SDK.

## Advanced Configuration

Model request parameters are implemented in `withdrawal/agent.py`; workflow review and retry limits are implemented in `withdrawal/review.py` and `withdrawal/core.py`. They are code settings, not supported `.env` options. There is no `DEBUG` environment switch in the launcher.

`make logs` reports managed process status. Streamlit and launcher output appear in the launch terminal; customer-service subprocess output is suppressed by `run_demo.py`.

## Troubleshooting configuration

Check your provider key locally without sharing it. Use **Load available models** to confirm access and select available models for each role. If a request fails, check the endpoint, account quota, and network connection.

See [Getting Started](getting-started.md) and [Troubleshooting](troubleshooting.md).
