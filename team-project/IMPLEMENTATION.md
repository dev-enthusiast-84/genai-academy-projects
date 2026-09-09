# Full Implementation Guide: Content Strategist MVP

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [API Specification (OpenAPI)](#api-specification)
4. [Database Schema](#database-schema)
5. [Implementation Steps](#implementation-steps)
6. [Cloud Deployment (GCP)](#cloud-deployment)
7. [Demo Walkthrough](#demo-walkthrough)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js)                   │
│  (Vercel)                                                    │
│  - Input form (paste content)                               │
│  - Show recommendations                                      │
│  - Display draft                                             │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTPS
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   Backend (FastAPI)                          │
│  (Cloud Run - Google Cloud)                                 │
│  ├─ POST /analyze (content strategy)                        │
│  ├─ POST /create-draft (content generation)                 │
│  └─ GET /health (monitoring)                               │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ├─ Claude API (LLM calls)
                   ├─ PostgreSQL (Supabase) - Content + Metadata
                   └─ CSV File (Performance Memory - Git-versioned)
```

---

## Project Structure

```
content-strategist/
├── backend/
│   ├── app.py                          # FastAPI app entry point
│   ├── main.py                         # Uvicorn runner
│   ├── requirements.txt                # Dependencies
│   ├── Dockerfile                      # Cloud Run container
│   ├── .env.example                    # Environment variables template
│   │
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── strategist.py               # Recommendation engine
│   │   └── creator.py                  # Draft generator
│   │
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py                 # SQLite/PostgreSQL wrapper
│   │   ├── memory.py                   # Performance memory loader
│   │   └── memory.csv                  # Hardcoded past posts
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py                  # Pydantic models (request/response)
│   │
│   └── utils/
│       ├── __init__.py
│       └── claude_client.py            # Anthropic SDK wrapper
│
├── frontend/
│   ├── pages/
│   │   ├── index.js                    # Main UI
│   │   ├── _app.js                     # Next.js app wrapper
│   │   └── api/
│   │       └── proxy.js                # Optional: API proxy (if same domain)
│   │
│   ├── components/
│   │   ├── ContentForm.js              # Input form
│   │   ├── RecommendationDisplay.js    # Show recommendation
│   │   └── DraftEditor.js              # Draft review & edit
│   │
│   ├── styles/
│   │   ├── globals.css
│   │   └── Home.module.css
│   │
│   ├── next.config.js
│   ├── package.json
│   └── .env.local                      # API URL
│
├── .github/
│   └── workflows/
│       └── deploy.yml                  # GitHub Actions CI/CD
│
├── docker-compose.yml                  # Local dev: backend + db
├── .gitignore
├── README.md                           # Setup & deployment guide
└── DEPLOYMENT.md                       # Cloud deployment steps
```

---

## API Specification (OpenAPI)

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://content-api.example.com`

### Endpoints

#### 1. POST /analyze
**Analyze content and get recommendation**

**Request:**
```json
{
  "content": "Just shipped a new feature for real-time collaboration in our SaaS app. Spent 3 months on this. Open to feedback!",
  "content_type": "linkedin_post"  // Optional
}
```

**Response:**
```json
{
  "request_id": "uuid-here",
  "status": "success",
  "data": {
    "recommendation": {
      "action": "repurpose",  // publish | repurpose | rework | combine | skip
      "reason": "Long-form product updates perform well with your audience (avg 2000 impressions). Suggest converting this into a blog post with detailed implementation walkthrough.",
      "confidence": 0.85,
      "suggested_format": "blog_post",
      "suggested_platform": "substack",
      "similar_posts": [
        {
          "id": "post_123",
          "title": "Building Real-Time Features",
          "performance": {
            "impressions": 2100,
            "engagement_rate": 0.12
          }
        }
      ]
    }
  }
}
```

**Error Response:**
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Content is empty"
  }
}
```

---

#### 2. POST /create-draft
**Generate draft content based on recommendation**

**Request:**
```json
{
  "content": "Just shipped real-time collaboration...",
  "recommendation": "repurpose",
  "format": "blog_post",
  "voice_style": "technical_but_accessible"  // Optional
}
```

**Response:**
```json
{
  "request_id": "uuid-here",
  "status": "success",
  "data": {
    "draft": {
      "title": "How We Built Real-Time Collaboration into Our SaaS Platform",
      "body": "Over the past three months, our team worked on implementing real-time collaboration features. Here's what we learned...",
      "format": "blog_post",
      "word_count": 1240,
      "reading_time_minutes": 5,
      "quality_metrics": {
        "tone_consistency": 0.92,
        "readability_score": 8.5,
        "engagement_potential": "high"
      }
    }
  }
}
```

---

#### 3. POST /save-decision
**Save user's decision (for feedback loop)**

**Request:**
```json
{
  "content_id": "post_123",
  "decision": "approved",  // approved | edited | rejected | published
  "feedback": "Great recommendation, added more technical depth",
  "performance_data": {
    "impressions": 3200,
    "engagement_rate": 0.15
  }  // Optional: update with real performance later
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Decision saved. Memory updated."
}
```

---

#### 4. GET /health
**Health check for monitoring**

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "claude_api": "ok",
    "database": "ok",
    "memory_file": "ok"
  }
}
```

---

## Database Schema

### Table: content
Stores user-uploaded content and metadata.

```sql
CREATE TABLE content (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  original_text TEXT NOT NULL,
  extracted_topics TEXT,  -- JSON: ["AI", "SaaS", "product"]
  tone TEXT,  -- professional, casual, technical, etc.
  source TEXT,  -- linkedin_paste, webinar_notes, draft
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_content_user_id ON content(user_id);
CREATE INDEX idx_content_created_at ON content(created_at DESC);
```

### Table: decisions
Tracks all user decisions (for feedback loop).

```sql
CREATE TABLE decisions (
  id TEXT PRIMARY KEY,
  content_id TEXT NOT NULL REFERENCES content(id),
  action TEXT NOT NULL,  -- approved, edited, rejected, published
  recommendation TEXT,  -- JSON: stored recommendation
  feedback TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (content_id) REFERENCES content(id)
);

CREATE INDEX idx_decisions_content_id ON decisions(content_id);
```

### Table: performance_metrics
Real performance data (populated later when integrated with LinkedIn/Substack).

```sql
CREATE TABLE performance_metrics (
  id TEXT PRIMARY KEY,
  content_id TEXT NOT NULL REFERENCES content(id),
  platform TEXT,  -- linkedin, substack, twitter
  impressions INTEGER,
  reactions INTEGER,
  comments INTEGER,
  shares INTEGER,
  engagement_rate DECIMAL,
  recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (content_id) REFERENCES content(id)
);
```

### Performance Memory (CSV)
For MVP, use a CSV file (git-versioned) with hardcoded past posts.

```csv
post_id,title,topics,tone,platform,format,impressions,reactions,comments,shares,engagement_rate,published_date
post_001,"AI is the Future","AI, future, tech","technical","LinkedIn","short_post",1500,250,45,20,0.196,2024-01-15
post_002,"Deep Dive: LLM Fine-tuning","AI, LLMs, engineering","technical","LinkedIn","long_article",800,120,35,15,0.194,2024-01-20
post_003,"Monday Motivation","mindset, motivation","casual","LinkedIn","quote",2000,50,5,2,0.027,2024-01-22
post_004,"My Productivity Workflow","workflow, tools, tips","casual","LinkedIn","video",500,200,100,50,0.6,2024-01-25
post_005,"Industry Hot Take","industry, opinion, tech","opinionated","LinkedIn","opinion",300,150,45,30,0.65,2024-02-01
```

---

## Implementation Steps

### Step 1: Backend Setup (2 hours)

#### 1a. Initialize Python Project
```bash
mkdir content-strategist-backend
cd content-strategist-backend

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
anthropic==0.7.1
python-dotenv==1.0.0
pydantic==2.5.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-multipart==0.0.6
cors==1.0.1
EOF

pip install -r requirements.txt
```

#### 1b. Create .env.example
```env
# Anthropic
ANTHROPIC_API_KEY=your_key_here

# Database (PostgreSQL/Supabase)
DATABASE_URL=postgresql://user:password@localhost/content_strategist

# Optional: SQLite for local dev
USE_SQLITE=true
SQLITE_DB_PATH=./content_strategist.db

# Server
API_HOST=0.0.0.0
API_PORT=8000
ENVIRONMENT=development

# CORS
FRONTEND_URL=http://localhost:3000
```

#### 1c. Create app.py (Main FastAPI App)
```python
# backend/app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from agents.strategist import strategist_analyze
from agents.creator import creator_generate_draft
from storage.database import init_db, add_content, add_decision
from storage.memory import load_performance_memory
from utils.claude_client import test_claude_connection

load_dotenv()

app = FastAPI(
    title="Content Strategist API",
    version="1.0.0",
    description="AI-powered content strategy and generation"
)

# CORS Configuration
origins = [
    os.getenv("FRONTEND_URL", "http://localhost:3000"),
    "http://localhost:3000",
    "https://*.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup():
    init_db()
    # Test Claude API connection
    try:
        test_claude_connection()
        print("✓ Claude API connected")
    except Exception as e:
        print(f"✗ Claude API error: {e}")

# Models
class AnalyzeRequest(BaseModel):
    content: str
    content_type: str = "linkedin_post"

class CreateDraftRequest(BaseModel):
    content: str
    recommendation: str
    format: str = "blog_post"
    voice_style: str = "professional"

# Endpoints
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0"
    }

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    """
    Analyze content and return strategic recommendation
    """
    if not req.content or len(req.content) < 10:
        raise HTTPException(status_code=400, detail="Content must be at least 10 characters")

    try:
        # Load performance memory
        memory = load_performance_memory()

        # Get recommendation from strategist agent
        recommendation = await strategist_analyze(req.content, memory)

        # Save to database
        content_id = add_content(
            content=req.content,
            content_type=req.content_type
        )

        return {
            "status": "success",
            "request_id": content_id,
            "data": {
                "recommendation": recommendation
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-draft")
async def create_draft(req: CreateDraftRequest):
    """
    Generate draft content based on recommendation
    """
    try:
        memory = load_performance_memory()
        
        draft = await creator_generate_draft(
            content=req.content,
            recommendation=req.recommendation,
            format=req.format,
            voice_style=req.voice_style,
            memory=memory
        )

        return {
            "status": "success",
            "data": {
                "draft": draft
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save-decision")
async def save_decision(decision_data: dict):
    """
    Save user decision for feedback loop
    """
    try:
        decision_id = add_decision(
            content_id=decision_data.get("content_id"),
            action=decision_data.get("decision"),
            feedback=decision_data.get("feedback")
        )
        return {"status": "success", "decision_id": decision_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000))
    )
```

---

### Step 2: Agents Implementation (3 hours)

#### 2a. Strategist Agent (backend/agents/strategist.py)
```python
# backend/agents/strategist.py
import json
from anthropic import Anthropic

client = Anthropic()

async def strategist_analyze(content: str, performance_memory: list) -> dict:
    """
    Analyze content against performance history and recommend action.
    """
    
    # Extract similar posts from memory
    similar_posts = find_similar_posts(content, performance_memory)
    
    # Build performance context
    performance_context = format_performance_data(similar_posts)
    
    # Call Claude
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        system="""You are a content strategy expert who helps creators maximize their impact.
        
        Analyze the given content and performance history. Recommend ONE action:
        - "publish": Post as-is, it matches high-performing content
        - "repurpose": Transform into a different format (newsletter, blog, thread)
        - "rework": Improve the current version before posting
        - "combine": Merge with another idea for more impact
        - "skip": Not aligned with audience preferences
        
        Respond with JSON only:
        {
          "action": "...",
          "reason": "...",
          "confidence": 0.85,
          "suggested_format": "blog_post",
          "suggested_platform": "substack"
        }
        """,
        messages=[{
            "role": "user",
            "content": f"""Content to analyze:
{content}

Your performance history (top similar posts):
{performance_context}

What should they do with this content?"""
        }]
    )
    
    # Parse JSON response
    response_text = response.content[0].text
    recommendation = json.loads(response_text)
    recommendation["similar_posts"] = similar_posts[:3]
    
    return recommendation

def find_similar_posts(content: str, memory: list, top_k: int = 5) -> list:
    """
    Find similar posts from memory using keyword matching.
    Later: replace with vector DB search.
    """
    keywords = extract_keywords(content)
    
    scored_posts = []
    for post in memory:
        score = 0
        post_topics = post.get("topics", "").split(",")
        for keyword in keywords:
            if any(keyword.lower() in topic.lower() for topic in post_topics):
                score += 1
        if score > 0:
            scored_posts.append((post, score))
    
    scored_posts.sort(key=lambda x: x[1], reverse=True)
    return [post for post, _ in scored_posts[:top_k]]

def extract_keywords(text: str, num_keywords: int = 5) -> list:
    """
    Extract key topics from text (simple version).
    Later: use Claude for smarter extraction.
    """
    # Very basic: split and filter
    words = text.lower().split()
    # In production: filter stopwords, use NLP
    return words[:num_keywords]

def format_performance_data(posts: list) -> str:
    """
    Format performance data for LLM context.
    """
    formatted = []
    for post in posts:
        formatted.append(
            f"- '{post['title']}' ({post['topics']}): "
            f"{post['impressions']} impressions, "
            f"{post['engagement_rate']*100:.1f}% engagement"
        )
    return "\n".join(formatted)
```

#### 2b. Creator Agent (backend/agents/creator.py)
```python
# backend/agents/creator.py
import json
from anthropic import Anthropic

client = Anthropic()

async def creator_generate_draft(
    content: str,
    recommendation: str,
    format: str,
    voice_style: str,
    memory: list
) -> dict:
    """
    Generate a draft in user's style based on approved recommendation.
    """
    
    # Get voice samples (first 3 posts as style reference)
    voice_samples = memory[:3]
    voice_context = format_voice_samples(voice_samples)
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1500,
        system=f"""You are a professional content writer who specializes in creating high-quality content.
        
        Write content that matches the given voice and style. The content should be:
        - Authentic and personal
        - Engaging for the target audience
        - Optimized for the specified format
        - Free of AI-generated clichés
        
        Voice/Style Reference:
        {voice_context}
        
        Respond with JSON only:
        {{
          "title": "...",
          "body": "...",
          "format": "{format}",
          "word_count": 0,
          "reading_time_minutes": 0,
          "quality_metrics": {{
            "tone_consistency": 0.9,
            "readability_score": 8.5,
            "engagement_potential": "high"
          }}
        }}
        """,
        messages=[{
            "role": "user",
            "content": f"""Original content:
{content}

Strategy: {recommendation}
Format: {format}
Voice style: {voice_style}

Generate a high-quality draft."""
        }]
    )
    
    response_text = response.content[0].text
    draft = json.loads(response_text)
    
    # Calculate reading time
    word_count = len(draft.get("body", "").split())
    draft["word_count"] = word_count
    draft["reading_time_minutes"] = max(1, word_count // 200)
    
    return draft

def format_voice_samples(posts: list) -> str:
    """
    Format voice samples for LLM to learn from.
    """
    samples = []
    for i, post in enumerate(posts[:3], 1):
        samples.append(f"Sample {i} ('{post['title']}', {post['tone']} tone):")
        # In real scenario, store full post text; here just show metadata
        samples.append(f"  Topics: {post['topics']}")
        samples.append(f"  Performance: {post['engagement_rate']*100:.0f}% engagement")
    
    return "\n".join(samples)
```

---

### Step 3: Frontend Setup (2 hours)

#### 3a. Create Next.js Project
```bash
npx create-next-app@latest frontend --typescript --tailwind
cd frontend
```

#### 3b. Main Page (pages/index.js)
```javascript
// frontend/pages/index.js
import { useState } from 'react';
import ContentForm from '../components/ContentForm';
import RecommendationDisplay from '../components/RecommendationDisplay';
import DraftEditor from '../components/DraftEditor';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [step, setStep] = useState('input'); // input | recommendation | draft
  const [content, setContent] = useState('');
  const [recommendation, setRecommendation] = useState(null);
  const [draft, setDraft] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async (inputContent) => {
    setLoading(true);
    setError(null);
    
    try {
      const res = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: inputContent })
      });

      if (!res.ok) throw new Error('Failed to analyze');
      
      const data = await res.json();
      setContent(inputContent);
      setRecommendation(data.data.recommendation);
      setStep('recommendation');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDraft = async (approvedRecommendation) => {
    setLoading(true);
    
    try {
      const res = await fetch(`${API_URL}/create-draft`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content,
          recommendation: approvedRecommendation.action,
          format: approvedRecommendation.suggested_format
        })
      });

      if (!res.ok) throw new Error('Failed to create draft');
      
      const data = await res.json();
      setDraft(data.data.draft);
      setStep('draft');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePublish = async () => {
    alert('✓ Draft ready to publish! (Demo: publishing mocked)');
    // In production: save decision via /save-decision endpoint
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-3xl mx-auto">
        <header className="text-center mb-8 pt-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Content Strategist</h1>
          <p className="text-gray-600">AI-powered recommendations to maximize your content impact</p>
        </header>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {step === 'input' && (
          <ContentForm onAnalyze={handleAnalyze} loading={loading} />
        )}

        {step === 'recommendation' && recommendation && (
          <RecommendationDisplay
            recommendation={recommendation}
            onApprove={handleCreateDraft}
            loading={loading}
          />
        )}

        {step === 'draft' && draft && (
          <DraftEditor draft={draft} onPublish={handlePublish} />
        )}
      </div>
    </div>
  );
}
```

#### 3c. Components (Example: ContentForm)
```javascript
// frontend/components/ContentForm.js
import { useState } from 'react';

export default function ContentForm({ onAnalyze, loading }) {
  const [content, setContent] = useState('');

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-2xl font-semibold mb-4">Share Your Content</h2>
      
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Paste a LinkedIn post, draft, or idea here..."
        className="w-full h-48 p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
      />

      <button
        onClick={() => onAnalyze(content)}
        disabled={loading || !content.trim()}
        className="mt-4 bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Analyzing...' : 'Get Recommendation'}
      </button>
    </div>
  );
}
```

---

### Step 4: Local Development Setup (30 mins)

#### 4a. Docker Compose (for local PostgreSQL)
```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: strategist
      POSTGRES_PASSWORD: localdev
      POSTGRES_DB: content_strategist
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### 4b. Run Locally
```bash
# Terminal 1: Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
# Should see: "Uvicorn running on http://0.0.0.0:8000"

# Terminal 2: Frontend
cd frontend
npm install
npm run dev
# Should see: "localhost:3000"

# Terminal 3 (optional): Database
docker-compose up
```

---

## Cloud Deployment (GCP)

### Step 1: Prepare Docker Image

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Step 2: Deploy Backend to Cloud Run

```bash
# 1. Authenticate with GCP
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Build and push to Artifact Registry
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/content-strategist-api

# 3. Deploy to Cloud Run
gcloud run deploy content-api \
  --image gcr.io/YOUR_PROJECT_ID/content-strategist-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="ANTHROPIC_API_KEY=YOUR_KEY,DATABASE_URL=YOUR_SUPABASE_URL"

# Output: https://content-api-xxx.a.run.app
```

### Step 3: Deploy Frontend to Vercel

```bash
# 1. Push to GitHub
git add .
git commit -m "Initial commit"
git push origin main

# 2. Connect to Vercel
# - Go to vercel.com
# - Click "Add New" > "Project"
# - Import your GitHub repo
# - Set env var: NEXT_PUBLIC_API_URL=https://content-api-xxx.a.run.app
# - Deploy

# Output: https://your-project.vercel.app
```

### Step 4: Configure Supabase (PostgreSQL)

```bash
# 1. Go to supabase.com, create project
# 2. Get DATABASE_URL from settings
# 3. Run migrations:

psql $DATABASE_URL << 'EOF'
-- Tables created here (see schema above)
EOF
```

---

## Demo Walkthrough

### Demo Scenario 1: Technical Content
**Input:**
```
Just launched a new feature for real-time collaboration in our SaaS app. 
Spent 3 months building it. We used WebSockets, Redis for state management, 
and PostgreSQL for persistence. Would love feedback!
```

**Expected Output:**
1. Recommendation: **"Repurpose"** → "Turn into a blog post with technical deep-dive"
2. Reason: "Technical product updates with implementation details perform best with your audience (avg 2100 impressions, 12% engagement)"
3. Draft Generated: "How We Built Real-Time Collaboration Features" (1200 words)

### Demo Scenario 2: Opinion/Hot Take
**Input:**
```
The AI hype cycle is ridiculous. 90% of startup ideas don't need ML. 
We're solving actual problems, not chasing trends.
```

**Expected Output:**
1. Recommendation: **"Publish"** → "Post as-is"
2. Reason: "Opinionated takes on industry trends generate high engagement with your audience (avg 300 impressions, 65% engagement). Your audience loves contrarian takes."
3. Draft: Show edited version (more nuanced, less aggressive)

### Demo Scenario 3: Personal/Lifestyle
**Input:**
```
Found a new productivity system that actually works for me: deep work blocks, 
no meetings before noon, one big task per day.
```

**Expected Output:**
1. Recommendation: **"Rework"** → "Add more specific examples and data"
2. Reason: "Personal experiences perform OK, but adding metrics/specific examples increases engagement by 40%"
3. Draft: "My Surprisingly Simple Productivity System (And Why It Works)"

---

## Open Specifications for Extension

### Future: Vector Database Integration
```python
# Replace keyword search with embeddings
from pinecone import Pinecone

pc = Pinecone(api_key=PINECONE_API_KEY)

# Later: Embed all posts
embeddings = embed_posts(performance_memory)
pc.upsert(embeddings)

# Later: Search
def find_similar_posts_v2(content: str, memory: list):
    query_embedding = embed_text(content)
    results = pc.query(query_embedding, top_k=5)
    return results
```

### Future: LangGraph Orchestration
```python
# Current: Direct agent calls
# Future: State machine orchestration

from langgraph.graph import StateGraph

workflow = StateGraph()
workflow.add_node("strategist", strategist_node)
workflow.add_node("creator", creator_node)
workflow.add_node("reviewer", reviewer_node)

workflow.add_edge("strategist", "creator")
workflow.add_conditional_edges("creator", route_to_review)

app = workflow.compile()
result = app.invoke({"content": user_content})
```

### Future: Real Data Collection
```python
# Add LinkedIn integration
from linkedin_api import Linkedin

def collect_performance_data():
    linkedin = Linkedin()
    posts = linkedin.get_posts(user_id)
    for post in posts:
        update_performance_metrics(
            post_id=post.id,
            impressions=post.impressions,
            engagement=post.comments + post.shares
        )
```

---

## Summary

**MVP Scope (Day 1):**
- ✓ FastAPI backend with 2 agents
- ✓ Next.js frontend
- ✓ SQLite database
- ✓ Hardcoded performance memory
- ✓ Deploy to Vercel + Cloud Run

**Production Extensions (Week 2-4):**
- Add vector DB (Pinecone)
- Add Voice Reviewer agent
- Switch to PostgreSQL
- Integrate LinkedIn API
- Add user authentication

**Full System (Month 2-3):**
- Multi-user support
- Real-time performance tracking
- Dashboard & analytics
- Fine-tuned voice model

---

**Next Steps:**
1. Clone the template repo: `git clone [repo-url]`
2. Follow "Local Development Setup" to run locally
3. Test with demo scenarios above
4. Deploy to GCP (backend) + Vercel (frontend)
5. Share live link with judges
