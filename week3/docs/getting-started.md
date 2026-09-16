# Getting Started

Get up and running with Recall in minutes.

## Prerequisites

### System Requirements

- **OS**: macOS, Linux, or Windows with WSL
- **Python**: 3.9 or higher
- **RAM**: 8GB minimum (16GB recommended)
- **Disk**: 6GB for models + ~2GB for runtime

### Software to Install

1. **Python 3.9+** — Download from [python.org](https://www.python.org)
2. **Ollama** — Download from [ollama.ai](https://ollama.ai)
3. **Git** (optional) — For cloning the repo

## Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd week3
```

### Step 2: Install Python Dependencies

```bash
# Install base requirements
pip install -r requirements.txt

# Install LiteLLM (for LLM proxy)
pip install litellm
```

### Step 3: Download LLM Models

This step downloads the models that power the LLM agents:

```bash
# Download the models (first time only, ~4GB)
ollama pull phi
ollama pull orca-mini
```

Models available locally:
```bash
ollama list
```

Expected output:
```
NAME              ID              SIZE
phi:latest        e2fd63...       1.6 GB
orca-mini:latest  2dbd9f...       2.0 GB
```

### Step 4: Verify Setup

Check that everything is installed:

```bash
# Check Python
python3 --version

# Check Ollama
ollama --version

# Check LiteLLM
pip list | grep litellm
```

## Running the App

### Option 1: Using Make (Recommended)

```bash
make start
```

This single command:
1. ✅ Stops any existing processes
2. ✅ Starts LiteLLM proxy in background
3. ✅ Starts Recall app
4. ✅ Opens dashboard at http://127.0.0.1:8501

### Option 2: Manual Start

If you prefer manual control:

**Terminal 1 — Start LiteLLM proxy:**
```bash
litellm --model ollama/phi
```

**Terminal 2 — Start Recall app:**
```bash
python3 run_demo.py
```

## Accessing the Application

Once running, open your browser and visit:

| Service | URL |
|---------|-----|
| **Recall Dashboard** | http://127.0.0.1:8501 |
| **Club Portal** | http://127.0.0.1:8101 |
| **Class Booking** | http://127.0.0.1:8102 |
| **Member Offers** | http://127.0.0.1:8103 |

The dashboard will show:
- Model configuration
- Service status
- Demo controls
- Data investigation interface

## First Time Walkthrough

### 1. Give Consent

1. Click **"1 · Club Portal"** button
2. This opens http://127.0.0.1:8101
3. Review the questionnaire
4. Click **"Give Consent"** to share your data
5. Return to Recall Dashboard

### 2. Investigate Data

1. Back in Recall Dashboard
2. Click **"Investigate data trail"**
3. Watch as the LLM agent team:
   - 🔍 Discovers your records
   - 📊 Traces dependencies
   - 📋 Reviews the proposal
4. Review the proposed withdrawal plan

### 3. Approve Withdrawal

1. Review the evidence trail
2. Check "I approve these deletions"
3. Click **"Approve & withdraw"**
4. Watch the deletion happen
5. Verify records are gone

### 4. Verify Removal

Once deletion completes:
- System checks all three services
- Confirms your data is absent
- Blocks re-ingestion
- Shows verification receipt

## Available Commands

### Using Makefile

```bash
# Start everything
make start

# Start individual components
make llm              # Start LiteLLM only
make app              # Start Recall only

# Management
make stop             # Stop all processes
make kill             # Force kill all
make logs             # View running processes
make clean            # Clean caches
make reset            # Full reset

# Help
make help             # Show all commands
```

### Manual Commands

```bash
# Start LiteLLM proxy
litellm --model ollama/phi

# Start Recall
python3 run_demo.py

# Run tests
pytest tests/

# View configuration
cat .env
```

## Troubleshooting

### Issue: "Ollama not found"

```bash
# Install Ollama from https://ollama.ai
# Or verify it's in your PATH:
which ollama
```

### Issue: "Port already in use"

```bash
# Kill all Recall processes
make kill

# Wait a moment
sleep 3

# Restart
make start
```

### Issue: Models not downloading

```bash
# Check Ollama is running and accessible
ollama ps

# Try downloading again
ollama pull phi --verbose
```

### Issue: LiteLLM won't start

```bash
# Check if litellm is installed
pip list | grep litellm

# Reinstall if needed
pip install --upgrade litellm
```

### Issue: Slow performance

- Ensure you have 8GB+ RAM free
- Close other applications
- Use Ollama's resource settings
- Models will warm up after first use

## Next Steps

- **[Architecture Overview](architecture.md)** — Understand how it works
- **[Configuration Guide](configuration.md)** — Customize settings
- **[API Reference](api.md)** — Learn about LLM agents
- **[Troubleshooting](troubleshooting.md)** — Common issues & fixes

## Support

- Check [Troubleshooting](troubleshooting.md) for common issues
- Read [Configuration](configuration.md) for setup details
- See [Contributing](contributing.md) for development help

---

**Ready?** Run `make start` and open http://127.0.0.1:8501
