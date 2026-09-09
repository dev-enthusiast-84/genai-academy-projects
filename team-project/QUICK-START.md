# Quick Start - Content Strategist MVP

**Get a working demo running in < 5 minutes.**

## Prerequisites

- Docker + Docker Compose (OR Python 3.11 + Node 18)
- `.env.local` file (copy from `.env.example`)

## Option 1: Docker (Recommended)

```bash
# Start everything
make dev-local

# Open browser
open http://localhost:3000
```

That's it! Backend, frontend, and database all run in containers.

---

## Option 2: Manual Setup (Local)

### 1. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs on `http://localhost:8000`

### 2. Frontend Setup (new terminal)

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000`

---

## What Works

### ✅ Full 4-Step Workflow

1. **Step 1: Input** - Paste content
2. **Step 2: Recommendation** - Strategist analyzes (mock response)
3. **Step 3: Draft** - Creator generates draft (mock response)
4. **Step 4: Review** - Reviewer scores quality (mock response)

### ✅ API Endpoints

- `GET /health` - System status & LLM config
- `POST /analyze` - Strategist agent
- `POST /create-draft` - Creator agent
- `POST /review` - Reviewer agent

### ✅ Frontend Features

- Multi-step workflow UI
- Progress bar
- Mock LLM responses
- Error handling
- Clean, responsive design

---

## What's NOT Implemented Yet

❌ Real LLM calls (Kimi 3 / Claude 3.5)  
❌ Vector similarity search (Pinecone)  
❌ Database (Supabase)  
❌ Observability (LangSmith, Sentry, PostHog)  
❌ Cloud deployment (Replit, Vercel)  

These will be added in Phase 2.

---

## Testing the Demo

### Scenario 1: Short Content

```
Input: "Just shipped v1!"
Expected: Action = "publish"
```

### Scenario 2: Medium Content

```
Input: "I've been thinking about AI systems. They're really useful..."
Expected: Action = "repurpose"
Draft: Multi-platform strategy
```

### Scenario 3: Long Content

```
Input: [500+ word article]
Expected: Action = "combine"
Draft: Series strategy
```

---

## Logs

### Backend Logs

```bash
# Terminal where backend runs
uvicorn main:app --reload

# Look for:
# INFO: Strategist analysis (MVP mock)
# INFO: Creator draft (MVP mock)
# INFO: Reviewer assessment (MVP mock)
```

### Frontend Logs

```bash
# Browser console (F12)
# Shows API calls and responses
```

### Docker Logs

```bash
make dev-logs
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :3000  # Frontend
lsof -i :8000  # Backend

# Kill it
kill -9 <PID>
```

### Docker Won't Start

```bash
# Remove old containers
docker-compose down

# Try again
make dev-local
```

### API Not Responding

```bash
# Check backend health
curl http://localhost:8000/health

# Should return:
# {
#   "status": "healthy",
#   "version": "0.1.0",
#   "dependencies": {...}
# }
```

---

## Next Steps

1. **Try the demo:**  
   `make dev-local` → Open http://localhost:3000

2. **Wire up real LLMs:**  
   Add ANTHROPIC_API_KEY and KIMI_API_KEY to .env.local  
   Update agents to use real LiteLLM calls

3. **Add database:**  
   Set up Supabase, add 15 golden posts, test similarity search

4. **Deploy:**  
   Push backend to Replit, frontend to Vercel

---

## Architecture

```
┌─────────────────────────────────────┐
│  Frontend (Next.js, localhost:3000) │
└────────────┬────────────────────────┘
             │ fetch()
             ▼
┌─────────────────────────────────────┐
│  Backend (FastAPI, localhost:8000)  │
│  ├─ /analyze (Strategist)           │
│  ├─ /create-draft (Creator)         │
│  └─ /review (Reviewer)              │
└────────────┬────────────────────────┘
             │ (mock responses for MVP)
             ▼
┌─────────────────────────────────────┐
│  LLM Models (TODO: Phase 2)          │
│  ├─ Kimi 3 (Strategist/Reviewer)    │
│  └─ Claude 3.5 (Creator)            │
└─────────────────────────────────────┘
```

---

## See Also

- `TECHNICAL-ARCHITECTURE.md` - Full architecture & decisions
- `docs/LLM-CONFIGURATION.md` - LLM setup guide
- `.env.example` - All configuration options

