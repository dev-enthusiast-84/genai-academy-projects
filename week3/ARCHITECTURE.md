# Recall - Architecture Overview

Complete system architecture documentation for Recall consent management dashboard.

## Quick Navigation

- **[Detailed Architecture](docs/architecture.md)** — System components and design
- **[Architecture Diagrams](docs/architecture-diagram.md)** — Visual system overview (ASCII diagrams)
- **[API Reference](docs/api.md)** — LLM agents and tool definitions
- **[Demo Guide](docs/demo-guide.md)** — Interactive workflow showcase

## System at a Glance

Recall is a **multi-agent LLM system** for managing data withdrawal with:

- **4 Specialized Agents**: Investigator, Scope Reviewer, Judge, Auditor
- **4 Customer Services**: Club Portal, Class Booking, Member Offers (+ Recall Dashboard)
- **Model APIs**: OpenAI or OpenRouter (provider charges may apply)
- **Verified Deletion**: Independent verification that data is actually gone

## Core Components

```
User Interface (Streamlit)
    ↓
Engine (Workflow Orchestration)
    ↓
LLM Agents (direct provider API)
    ↓
OpenAI or OpenRouter

Service APIs (Flask)
    ↓
SQLite Database (Local State)
```

## Key Features

### 🤖 Multi-Agent Reasoning
- **Investigator**: Discovers data dependencies
- **Scope Reviewer**: Validates proposals
- **Judge**: Evaluates against evidence
- **Auditor**: Verifies deletion succeeded

### 📊 Visual Workflow
- Evidence trail diagrams
- Service dependency graphs
- Real-time investigation progress
- Verification receipts

### 🔐 Privacy-First Design
- Authorized synthetic evidence is sent to the selected provider in live mode
- Real deletion (not soft deletes)
- Explicit approval gates
- Automated verification

### ⚡ Flexible Model Selection
- Configure models independently for each role
- Use a separate judge model to review proposals
- Swap models without restarting
- Compare quality across models

## Architecture Highlights

### Isolation & Safety
- Single-user demo (easily extensible)
- Explicit approval required for deletion
- Retry logic (up to 3 attempts per record)
- Request expiration (24 hours)

### Extensibility
- Add new services easily
- Define new LLM tools
- Customize workflows
- Plug in different LLM providers

### Observability
- Complete audit trail
- Agent findings logged
- Deletion timeline
- Verification reports

## Next Steps

1. **Understand the Flow** → [Demo Guide](docs/demo-guide.md)
2. **Deep Dive into Design** → [Architecture Details](docs/architecture.md)
3. **See the Diagrams** → [ASCII Diagrams](docs/architecture-diagram.md)
4. **Learn the API** → [API Reference](docs/api.md)
5. **Get Started** → [Getting Started Guide](docs/getting-started.md)

## Quick Commands

```bash
# Start everything
make demo

# Run interactive showcase
make showcase

# View available models
make demo-models

# See all commands
make help
```

## Tech Stack

- **Frontend**: Streamlit (Python)
- **LLM**: OpenAI or OpenRouter (direct API)
- **Services**: Flask (Python)
- **Database**: SQLite (local)
- **Build**: Makefile (consolidated commands)

---

**For complete technical details, see [Architecture](docs/architecture.md)**
