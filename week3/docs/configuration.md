# Configuration Guide

Configure Recall for your needs.

## Environment Variables

Configuration is managed through the `.env` file. Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

## LLM Configuration

### Provider Selection

```env
# Use LiteLLM (recommended for local models)
LLM_PROVIDER=litellm
LLM_BASE_URL=http://localhost:4000/v1
LLM_API_KEY=sk-1234

# OR use OpenRouter (requires API credits)
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-...
```

### Model Selection

Assign different models to each agent role:

```env
# Investigator: Discovers records, traces lineage
LLM_INVESTIGATOR_MODEL=ollama/phi

# Scope Reviewer: Reviews & challenges proposals
LLM_SCOPE_REVIEWER_MODEL=ollama/orca-mini

# Judge: Evaluates proposals against evidence
LLM_JUDGE_MODEL=ollama/phi

# Auditor: Verifies outcomes, reports findings
LLM_AUDITOR_MODEL=ollama/phi
```

### Available Ollama Models

```bash
# View installed models
ollama list

# Pull additional models
ollama pull mistral
ollama pull neural-chat
ollama pull dolphin-mixtral
```

**Size & Performance:**

| Model | Size | Speed | Reasoning | Recommended For |
|-------|------|-------|-----------|-----------------|
| phi | 2.7GB | ⚡⚡⚡ | Good | Fast tasks |
| orca-mini | 2.0GB | ⚡⚡ | Better | Reviews |
| mistral | 5.0GB | ⚡⚡ | Good | General |
| neural-chat | 4.1GB | ⚡ | Good | Conversations |
| mixtral | 26GB | ⚡ | Excellent | Complex reasoning |

## API Configuration

### LiteLLM Proxy

Start the proxy with custom model:

```bash
# Default (phi)
litellm --model ollama/phi

# Custom model
litellm --model ollama/orca-mini

# With custom port
litellm --model ollama/phi --port 5000
```

Then update `.env`:
```env
LLM_BASE_URL=http://localhost:5000/v1
```

### OpenRouter

If using OpenRouter instead of local models:

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-your-key-here
LLM_INVESTIGATOR_MODEL=openai/gpt-5.4-mini
LLM_SCOPE_REVIEWER_MODEL=anthropic/claude-sonnet-4.6
LLM_JUDGE_MODEL=openai/gpt-5.4-mini
LLM_AUDITOR_MODEL=anthropic/claude-sonnet-4.6
```

## Service Configuration

### Local Service Ports

```env
# Defined in withdrawal/services.py
# Club Portal: 8101
# Class Booking: 8102
# Member Offers: 8103
# Recall Dashboard: 8501
# LiteLLM Proxy: 4000
```

To use different ports, edit `run_demo.py`.

### Service URLs

```env
# Configured via environment during run_demo.py
RECALL_SERVICE_URLS={"documents":"http://127.0.0.1:8101","search":"http://127.0.0.1:8102",...}
RECALL_SERVICE_TOKEN=generated-at-runtime
```

## Database Configuration

### Runtime Directory

```env
# Default: .runtime/fitness-local
RECALL_DATA_DIR=.runtime/fitness-local

# Custom location
RECALL_DATA_DIR=/path/to/data
```

### Reset Database

To start fresh with demo data:

```bash
# Via Make
make reset

# Or manually
rm -rf .runtime
make start
```

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

Requires: `pip install -r requirements-mcp.txt`

## Advanced Configuration

### Model Parameters

```python
# In withdrawal/agent.py, ModelClient.complete()

payload = {
    'model': self.model,
    'messages': messages,
    'max_tokens': 1600,  # Adjust inference length
    'temperature': 0.7,  # Adjust creativity (0-1)
    'top_p': 0.9,        # Nucleus sampling
}
```

### Workflow Parameters

```python
# In withdrawal/core.py, Engine class

# Max investigation rounds
INVESTIGATION_ROUNDS = 2

# Max repair/correction rounds
REPAIR_ROUNDS = 2

# Request TTL
REQUEST_EXPIRY_HOURS = 24

# Max retry attempts per record
MAX_RETRIES = 3
```

### Logging Configuration

```python
# Set environment variable
export DEBUG=true

# Or in Python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Common Configurations

### Development Setup

```env
LLM_PROVIDER=litellm
LLM_BASE_URL=http://localhost:4000/v1
LLM_API_KEY=sk-1234
LLM_INVESTIGATOR_MODEL=ollama/phi
LLM_SCOPE_REVIEWER_MODEL=ollama/phi
LLM_JUDGE_MODEL=ollama/phi
LLM_AUDITOR_MODEL=ollama/phi
RECALL_TOOL_TRANSPORT=http
NOTIFICATION_ENABLED=false
```

### Production Setup (Example)

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-...
LLM_INVESTIGATOR_MODEL=openai/gpt-4
LLM_SCOPE_REVIEWER_MODEL=anthropic/claude-opus
LLM_JUDGE_MODEL=openai/gpt-4
LLM_AUDITOR_MODEL=anthropic/claude-opus

NOTIFICATION_ENABLED=true
NOTIFICATION_PROVIDER=email
NOTIFICATION_SMTP_HOST=smtp.gmail.com
NOTIFICATION_SMTP_USERNAME=notifications@company.com
NOTIFICATION_SMTP_PASSWORD=app-password

RECALL_DATA_DIR=/var/lib/recall/data
```

### Low-Resource Setup (Minimal)

```env
# Use smallest models
LLM_PROVIDER=litellm
LLM_BASE_URL=http://localhost:4000/v1
LLM_INVESTIGATOR_MODEL=ollama/tinyllama
LLM_SCOPE_REVIEWER_MODEL=ollama/tinyllama
LLM_JUDGE_MODEL=ollama/tinyllama
LLM_AUDITOR_MODEL=ollama/tinyllama
```

Then: `ollama pull tinyllama`

## Troubleshooting Configuration

### Models Not Found

```bash
# List available models
ollama list

# Install missing model
ollama pull model-name
```

### API Key Errors

Verify your `.env` file:
```bash
grep "OPENROUTER_API_KEY\|LLM_API_KEY" .env
```

Keys should start with proper prefix:
- OpenRouter: `sk-or-v1-...`
- LiteLLM: `sk-1234` (dummy for local)

### Port Conflicts

If ports are in use:

```bash
# Find what's using port 4000
lsof -i :4000

# Kill process
kill -9 <PID>

# Use different port
litellm --port 5000
```

### Model Memory Issues

If models are slow or crash:

1. Check available RAM: `free -h`
2. Use smaller models (phi instead of mixtral)
3. Close other applications
4. Increase system swap

---

**Next**: [Getting Started](getting-started.md) | [Troubleshooting](troubleshooting.md)
