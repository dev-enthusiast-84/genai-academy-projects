# Recall - Consent Management Dashboard

A privacy-first demonstration of data withdrawal consent management using LLM-powered investigation of data dependencies across distributed systems.

**Consent has an undo button** — Withdraw your data and verify it's actually gone.

Start the four connected apps with `./demo.sh` (stop an older demo with Ctrl+C first). The current workflow view is preserved; see [workflow recovery and verification](docs/RECOVERY.md).

---

## Quick Start

### Prerequisites

Before running the app, ensure you have:

- **Python 3.9+**
- **Ollama** (for running local LLM models)
- **LiteLLM** (for proxying LLM requests)

### 1. Install Ollama

Download and install from: https://ollama.ai

After installation, verify:
```bash
ollama --version
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
pip install litellm
```

### 3. Download Models

The app uses small, fast models. Pull them once:

```bash
ollama pull phi
ollama pull orca-mini
```

This downloads:
- **phi** (2.7GB) - Fast, lightweight model
- **orca-mini** (2.0GB) - Better reasoning for reviews

### 4. Start the App

Simply run:

```bash
make start
```

This starts both the LiteLLM proxy and Recall app automatically.

Once running, open your browser:
- **Recall Dashboard**: http://127.0.0.1:8501

---

## Available Commands

### Using the Makefile

```bash
# Start everything (LiteLLM proxy + Recall app)
make start

# Start only LiteLLM proxy (runs in background)
make llm

# Start only Recall app (if LiteLLM already running)
make app

# Stop all processes
make stop

# Force kill all processes
make kill

# View running processes and logs
make logs

# Clean up caches and runtime data
make clean

# Full reset (clean + stop)
make reset

# Show all available commands
make help
```

---

## URLs

Once running, access the demo at:

| Service | URL | Purpose |
|---------|-----|---------|
| **Recall Dashboard** | http://127.0.0.1:8501 | Main privacy investigation interface |
| **Club Portal** | http://127.0.0.1:8101 | Customer app #1 (documents) |
| **Class Booking** | http://127.0.0.1:8102 | Customer app #2 (search) |
| **Member Offers** | http://127.0.0.1:8103 | Customer app #3 (personalization) |

---

## Configuration

The app is configured via `.env` file with the following LLM agents:

```env
LLM_PROVIDER=litellm
LLM_BASE_URL=http://localhost:4000/v1
LLM_API_KEY=sk-1234

# Role-specific models
LLM_INVESTIGATOR_MODEL=ollama/phi
LLM_SCOPE_REVIEWER_MODEL=ollama/orca-mini
LLM_JUDGE_MODEL=ollama/phi
LLM_AUDITOR_MODEL=ollama/phi
```

### Model Roles

- **Investigator** (`phi`): Discovers records, traces lineage, inspects service state
- **Scope Reviewer** (`orca-mini`): Reviews proposals, challenges assumptions, ensures correctness
- **Judge** (`phi`): Evaluates proposals against evidence, identifies issues
- **Auditor** (`phi`): Verifies outcomes, reports findings

---

## Workflow

### 1. First Time Setup

1. Start the app with `make start`
2. Go to **Club Portal** (http://127.0.0.1:8101)
3. Give consent to share your questionnaire data
4. The other apps will show personalized content

### 2. Investigate & Withdraw

1. Return to **Recall Dashboard** (http://127.0.0.1:8501)
2. Click "Investigate data trail"
3. The LLM agent team will:
   - Discover which records contain your data
   - Trace dependencies across services
   - Build a withdrawal plan
4. Review the plan
5. Approve to delete and verify removal

### 3. Verify

After approval, the system:
- Deletes records from all connected services
- Verifies deletion was successful
- Blocks re-ingestion of your data

---

## Stopping the App

To stop all services:

```bash
make stop
```

To force kill if needed:

```bash
make kill
```

---

## Troubleshooting

### LiteLLM not starting

```bash
# Check if litellm is installed
pip list | grep litellm

# Reinstall if needed
pip install --upgrade litellm
```

### Models not found

```bash
# Check which models are installed
ollama list

# Pull missing models
ollama pull phi
ollama pull orca-mini
```

### Port already in use

If ports 8501, 8101-8103, or 4000 are already in use:

```bash
# Kill all related processes
make kill

# Wait a few seconds, then restart
sleep 3
make start
```

### Check running processes

```bash
make logs
```

This shows all Recall-related processes and recent LiteLLM logs.

---

## Project Structure

```
week3/
├── Makefile                 # Consolidated commands
├── README.md               # This file
├── .env                    # Configuration (LLM models, etc.)
├── app.py                  # Streamlit dashboard
├── run_demo.py            # Launch all services
├── requirements.txt        # Python dependencies
│
├── withdrawal/
│   ├── agent.py           # LLM agent client
│   ├── core.py            # Core withdrawal logic
│   ├── review.py          # Investigation & review flows
│   ├── services.py        # Connected service APIs
│   └── ...
│
├── data/
│   └── fitness.json       # Demo data (synthetic)
│
└── tests/
    └── ...                # Test suite
```

---

## Technology Stack

- **Frontend**: Streamlit
- **LLM Backend**: LiteLLM proxy + Ollama
- **Models**: Phi 2.7B, Orca-Mini 3B
- **Local Services**: Flask apps (documents, search, personalization)
- **Database**: SQLite (local)

---

## Notes

- **No external API costs**: Uses local Ollama models
- **Synthetic data**: All demo data is safe-to-experiment-with fitness club data
- **Real deletion**: Deletes are actually performed on local stores (not just marked)
- **Privacy-first**: No data leaves your machine unless you explicitly approve

---

## Next Steps

1. Run `make start` to begin
2. Visit http://127.0.0.1:8501
3. Follow the on-screen instructions
4. Experiment with data withdrawal workflows

Enjoy exploring consent-first data privacy! 🔐
