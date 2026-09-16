# Troubleshooting

Solutions for common issues.

## Installation Issues

### Python Version Mismatch

**Error:** `python: command not found` or wrong version

**Solution:**
```bash
# Check Python version
python3 --version

# Should be 3.9 or higher
# If not, install from python.org or use:
brew install python@3.11  # macOS
apt install python3.11    # Linux
```

### Dependencies Not Installing

**Error:** `pip install -r requirements.txt` fails

**Solution:**
```bash
# Upgrade pip first
pip install --upgrade pip

# Try installing individual packages
pip install streamlit httpx pytest

# Or use a virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### Ollama Not Found

**Error:** `ollama: command not found`

**Solution:**
1. Download Ollama: https://ollama.ai
2. Install and start the Ollama service
3. Verify: `ollama --version`

On macOS, Ollama runs as a background service after installation.

## Model Download Issues

### Models Stuck Downloading

**Error:** `ollama pull phi` hangs or times out

**Solution:**
```bash
# Cancel with Ctrl+C and retry
ollama pull phi

# Check progress
ollama list

# If still stuck, restart Ollama:
# macOS: System Preferences > Ollama > Restart
# Linux: sudo systemctl restart ollama
```

### Not Enough Disk Space

**Error:** `SQLITE_CANTOPEN` or "disk full"

**Solution:**
```bash
# Check disk space
df -h

# Models need ~6GB:
# phi: 1.6GB
# orca-mini: 2.0GB
# app runtime: 2GB

# Clean up if needed:
make clean
```

### Model Not Available

**Error:** `Model xyz not found` when starting app

**Solution:**
```bash
# List installed models
ollama list

# Pull the missing model
ollama pull phi
ollama pull orca-mini
```

## Startup Issues

### Port Already in Use

**Error:** `Address already in use` on port 8501, 4000, etc.

**Solution:**
```bash
# Find process using port
lsof -i :8501        # Recall
lsof -i :4000        # LiteLLM
lsof -i :8101-8103   # Services

# Kill the process
kill -9 <PID>

# Or kill all Recall processes
make kill

# Wait a moment
sleep 3

# Restart
make start
```

### LiteLLM Won't Start

**Error:** `litellm: command not found`

**Solution:**
```bash
# Verify installation
pip list | grep litellm

# Reinstall if needed
pip install --upgrade litellm

# Verify it works
litellm --help
```

### Services Won't Start

**Error:** `RuntimeError: A customer application exited during startup`

**Solution:**

Check if ports are available:
```bash
# These ports should be free:
# 8101, 8102, 8103, 8501, 4000

lsof -i :8101
lsof -i :8102
lsof -i :8103

# If used, free them:
make kill
sleep 3
make start
```

## Runtime Issues

### HTTP 402 Error

**Error:** `Provider returned HTTP 402. Check the endpoint, key, model access, and quota.`

**Cause:** OpenRouter account has no credits

**Solution:**
```bash
# Check your configuration
cat .env | grep PROVIDER

# If using OpenRouter:
# Go to https://openrouter.ai/settings/credits
# Add credits to your account

# Or switch to local models:
# Edit .env to use litellm + Ollama (free)
LLM_PROVIDER=litellm
LLM_BASE_URL=http://localhost:4000/v1
```

### Model Inference Timeout

**Error:** `timeout` when LLM calls happen

**Solution:**
```bash
# Check if Ollama is running
ollama ps

# Check model is loaded
ollama list

# If slow, model might be loading
# Wait 30-60 seconds for model to warm up

# Try smaller model
# Edit .env to use phi instead of mixtral
```

### Memory Issues

**Error:** `Out of memory` or system freezes

**Solution:**
```bash
# Check available RAM
free -h

# Free up memory
# Close other applications
# Stop other services:
make kill

# Use smaller models in .env:
LLM_INVESTIGATOR_MODEL=ollama/phi
LLM_SCOPE_REVIEWER_MODEL=ollama/phi
```

## Application Issues

### Dashboard Doesn't Load

**Error:** http://127.0.0.1:8501 shows blank page

**Solution:**

1. Check if Streamlit is running:
```bash
make logs
```

2. Check browser console for errors (F12)

3. Try hard refresh (Ctrl+Shift+R)

4. Restart the app:
```bash
make stop
make start
```

### Button Doesn't Work

**Error:** "Investigate data trail" button is grayed out

**Cause:** Model not selected or data not initialized

**Solution:**

1. Open sidebar (top-left menu)
2. Check if model is selected
3. Check if "Live agent" mode is selected
4. If starting fresh, document D1 might not exist yet

### Error: "Application rejected the scoped service request"

**Cause:** One of the three services (8101, 8102, 8103) is not responding

**Solution:**
```bash
# Restart everything
make kill
sleep 3
make start

# Check service health
curl http://127.0.0.1:8101/health
curl http://127.0.0.1:8102/health
curl http://127.0.0.1:8103/health
```

All should return `200 OK`.

## Data Issues

### Database Corrupted

**Error:** `SQLITE database image header` error

**Solution:**
```bash
# Reset demo data (fresh start)
make reset

# This removes .runtime folder and starts fresh
```

### Data Not Persisting

**Error:** Changes disappear on restart

**Cause:** Database file location issue

**Solution:**
```bash
# Check database location
ls -la .runtime/fitness-local/recall/

# Verify it exists:
ls .runtime/fitness-local/recall/recall.db

# If missing, run reset:
make reset
```

## Performance Issues

### Slow Inference

**Cause:** Large model or insufficient resources

**Solution:**
```bash
# Use smaller models
# Edit .env to use phi (2.7B) instead of mixtral (26GB)

# Or reduce max_tokens in agent.py
# Line ~77: 'max_tokens': 800  (reduce from 1600)
```

### High Memory Usage

**Solution:**
```bash
# Close other applications
# Monitor memory while running:
watch -n 1 free -h

# Use activity monitor / task manager to find hogs
# Restart if memory doesn't improve:
make kill
```

## LiteLLM Issues

### LiteLLM Not Finding Ollama

**Error:** `Error contacting http://127.0.0.1:11434`

**Solution:**
```bash
# Make sure Ollama is running
ollama serve

# OR if it's a service:
sudo systemctl start ollama  # Linux
# macOS: System Preferences > Ollama > Start

# Verify Ollama responds
curl http://127.0.0.1:11434/api/tags
```

### Models Not Available in LiteLLM

**Error:** `Model xyz not found`

**Solution:**
```bash
# Check Ollama models
ollama list

# Pull if missing
ollama pull phi

# Restart LiteLLM after pulling
make stop
sleep 2
make start
```

## Debugging

### Enable Debug Logging

```bash
# Set debug environment
export DEBUG=true
make start

# Or in Python:
python3 -c "import logging; logging.basicConfig(level=logging.DEBUG)"
```

### Check Running Processes

```bash
make logs

# Shows:
# - All Recall-related processes
# - Last 10 lines of LiteLLM log
```

### View Full Logs

```bash
# LiteLLM logs (if running in background)
tail -f .litellm.log

# Streamlit logs (appears in terminal)
# Check terminal where you ran 'make start'
```

### Test Individual Components

```bash
# Test Ollama
ollama ps
ollama list

# Test LiteLLM
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"ollama/phi","messages":[{"role":"user","content":"hi"}]}'

# Test Services
curl http://127.0.0.1:8101/health
curl http://127.0.0.1:8102/health
curl http://127.0.0.1:8103/health
```

## Getting Help

1. Check [Troubleshooting](troubleshooting.md) (this page)
2. Review [Configuration](configuration.md)
3. Check logs: `make logs`
4. See [Contributing](contributing.md) for reporting issues

---

**Still stuck?** Check the issue more carefully or ask for help.
