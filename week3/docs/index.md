# Recall - Consent Management Dashboard

Welcome to Recall, a privacy-first demonstration of data withdrawal consent management using LLM-powered investigation.

> **Consent has an undo button** — Withdraw your data and verify it's actually gone.

## What is Recall?

Recall is a working demonstration that shows how modern privacy-first systems can:

- 🔍 **Investigate** data dependencies across distributed services
- 📋 **Review** withdrawal proposals with multiple LLM agents
- ✅ **Verify** that data is actually deleted
- 🛡️ **Block** re-ingestion after withdrawal

## Quick Links

- **[Getting Started](getting-started.md)** — Installation & first run
- **[Architecture](architecture.md)** — System design & components
- **[API Reference](api.md)** — LLM agents & tool definitions
- **[Configuration](configuration.md)** — Environment setup
- **[Troubleshooting](troubleshooting.md)** — Common issues & fixes
- **[Contributing](contributing.md)** — Development guide

## Key Features

### 🤖 Multi-Agent LLM System

Four specialized LLM agents work together:

| Agent | Role | Model |
|-------|------|-------|
| **Investigator** | Discovers records, traces lineage | phi (2.7B) |
| **Scope Reviewer** | Reviews proposals, challenges assumptions | orca-mini (3B) |
| **Judge** | Evaluates proposals against evidence | phi (2.7B) |
| **Auditor** | Verifies outcomes, reports findings | phi (2.7B) |

### 🏗️ Distributed Services

Three independent customer applications demonstrate data sharing:

- **Club Portal** — Member questionnaires & preferences
- **Class Booking** — Personalized class recommendations
- **Member Offers** — Targeted promotions & deals

### 🔐 Privacy by Design

- No external data transmission (runs locally)
- Real deletion (not soft deletes)
- Explicit user approval required
- Automated verification after deletion

## The Workflow

```
1. CONSENT
   └─ Give consent in Club Portal
   
2. PERSONALIZATION
   └─ Data shared to Class Booking & Member Offers
   
3. WITHDRAWAL REQUEST
   └─ Request withdrawal in Recall Dashboard
   
4. INVESTIGATION
   └─ LLM agents discover & trace data
   
5. REVIEW
   └─ Multiple agents review the plan
   
6. APPROVAL
   └─ User approves withdrawal
   
7. EXECUTION
   └─ Delete records from all services
   
8. VERIFICATION
   └─ Confirm deletion completed
```

## Getting Started

### Minimum Requirements

- Python 3.9+
- Ollama (for local LLM models)
- 8GB+ RAM
- ~6GB disk space (for models)

### Installation (1 minute)

```bash
# 1. Clone and navigate
git clone <repo>
cd week3

# 2. Install dependencies
pip install -r requirements.txt
pip install litellm

# 3. Download models
ollama pull phi
ollama pull orca-mini

# 4. Start everything
make start
```

Then open: **http://127.0.0.1:8501**

## What Makes This Different?

### Traditional Approach ❌
- Manual data discovery
- No verification of deletion
- High privacy risk
- Time-consuming

### Recall Approach ✅
- Automated investigation
- Verified deletion
- Privacy-first design
- Minutes, not hours

## Technology Stack

- **Frontend**: Streamlit (reactive UI)
- **LLM Backend**: LiteLLM + Ollama (local inference)
- **Models**: Phi 2.7B, Orca-Mini 3B (open-source)
- **Services**: Flask (local APIs)
- **Database**: SQLite (local storage)

## Documentation

- [Getting Started](getting-started.md) - Setup & first run
- [Architecture](architecture.md) - System design
- [Configuration](configuration.md) - .env settings
- [API Reference](api.md) - Agent tools & workflows
- [Troubleshooting](troubleshooting.md) - Common issues
- [Contributing](contributing.md) - Development guide

## Live Demo

The project includes a fully functional demo with:

- Synthetic fitness club data
- Three independent service stores
- Realistic data sharing patterns
- End-to-end withdrawal workflows

No external dependencies or API keys required!

## Key Innovations

### 🧠 Multi-Agent Reasoning
Multiple LLM agents review proposals independently, catching errors before execution.

### 🔍 Dependency Tracing
Automated discovery of explicit data relationships across services.

### ✅ Verified Deletion
Post-deletion audits confirm data is actually gone, not just marked.

### 🛡️ Re-ingestion Blocking
Prevents data from being re-added after withdrawal.

## Use Cases

1. **GDPR Compliance** — Right to be forgotten
2. **Privacy Audits** — Verify data removal capabilities
3. **Privacy Engineering Research** — Study data workflows
4. **Privacy Product Development** — Test withdrawal mechanisms
5. **Privacy Education** — Teach consent & deletion concepts

## Performance

Typical workflow times (on modern laptop):

- Investigation: 30-60 seconds
- Review: 10-30 seconds
- Deletion: 5-10 seconds
- Verification: 10-20 seconds

**Total: ~2-3 minutes** (vs manual investigation: hours)

## Open Source & Local

✅ No cloud dependencies
✅ No API costs
✅ Fully open source
✅ Run everything locally
✅ No data leaves your machine

## Next Steps

1. **[Get Started](getting-started.md)** — Install & run
2. **[Learn the Architecture](architecture.md)** — Understand the design
3. **[Explore the Demo](getting-started.md#running-the-demo)** — Try it out
4. **[Contribute](contributing.md)** — Help improve it

---

**Questions?** Check [Troubleshooting](troubleshooting.md) or [Contributing](contributing.md).

**Ready to begin?** Start with [Getting Started](getting-started.md).
