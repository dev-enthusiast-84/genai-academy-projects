# Demo Guide - Interactive Workflow Showcase

Learn how to demonstrate Recall's data withdrawal workflow with real examples.

## Quick Start Demo (5 minutes)

### 1. Start Everything

```bash
make demo
```

This starts:
- ✅ LiteLLM proxy (localhost:4000)
- ✅ Club Portal (localhost:8101)
- ✅ Class Booking (localhost:8102)  
- ✅ Member Offers (localhost:8103)
- ✅ Recall Dashboard (localhost:8501)

### 2. Follow the Interactive Guide

```bash
make showcase
```

This displays step-by-step instructions for the complete workflow.

---

## Full Workflow Walkthrough

### Phase 1: Consent & Sharing (1 minute)

**Goal**: Give consent and see data shared to other services

#### Step 1.1: Visit Club Portal
- Open: http://127.0.0.1:8101
- See: Fitness questionnaire form
- Click: **"Give Consent"** button
- Result: Consent granted, data shared to other apps

#### Step 1.2: Verify Sharing
- Open: http://127.0.0.1:8102 (Class Booking)
  - See: Personalized class recommendations
  - Notice: "Evening Yoga" in your preferences
- Open: http://127.0.0.1:8103 (Member Offers)
  - See: Targeted offers based on your profile
  - Notice: Fitness-related promotions

**Key Point**: Your fitness questionnaire (D1) is now linked across three services via:
- D1 (questionnaire) → T1 (class preferences) → V1 (personalized offers)

### Phase 2: Investigation (2-3 minutes)

**Goal**: Use LLM agents to discover and trace data dependencies

#### Step 2.1: Select Models
- Open: http://127.0.0.1:8501 (Recall Dashboard)
- Sidebar - Model connection:
  - **Investigator**: `ollama/phi` (fast) ← default
  - **Scope Reviewer**: `ollama/orca-mini` (balanced)
  - **Judge**: `ollama/phi`
  - **Auditor**: `ollama/phi`
- Click: **"Load available models"** (optional)
- Result: Model dropdown shows available options

#### Step 2.2: Investigate Data Trail
- Main form: "What would you like withdrawn?"
- Pre-filled: "Withdraw my fitness-personalization consent for questionnaire D1..."
- Click: **"Investigate data trail"** button
- Watch: Investigation progress in status box
  1. Discovering records
  2. Tracing dependencies
  3. Inspecting service state

#### Step 2.3: Review Results
- See: Evidence trail diagram
  - CLUB PORTAL → CLASS BOOKING → MEMBER OFFERS
- See: Records panel
  - Club Portal: D1 (Present)
  - Class Booking: T1 (Present)
  - Member Offers: V1 (Present)

**What's Happening**:
- Investigator agent discovers D1, T1, V1
- Scope Reviewer checks the proposal
- Judge evaluates against evidence
- All findings displayed for your review

### Phase 3: Approval & Withdrawal (1 minute)

**Goal**: Approve and execute the withdrawal

#### Step 3.1: Review Proposal
- Right panel: "Your Control Point"
- Shows: Withdrawal receipt
- Displays: Exact records to be deleted
  - D1 (Questionnaire)
  - T1 (Class preferences)
  - V1 (Personalized offers)

#### Step 3.2: Approve Deletion
- Check: "I approve these deletions and re-ingestion blocks"
- Click: **"Approve & withdraw"** button
- Watch: Deletion happens in real-time
  - Status updates for each service
  - Timeline of events at bottom

### Phase 4: Verification (1 minute)

**Goal**: Verify deletion actually worked

#### Step 4.1: Check Services
After deletion completes:
- Open: http://127.0.0.1:8101 (Club Portal)
  - ❌ Your questionnaire is gone
- Open: http://127.0.0.1:8102 (Class Booking)
  - ❌ Your preferences are gone
- Open: http://127.0.0.1:8103 (Member Offers)
  - ❌ Your offers are gone

#### Step 4.2: View Receipt
- Back to: http://127.0.0.1:8501
- Right panel shows:
  - ✅ Withdrawal receipt
  - ✅ Verification status: "Withdrawal verified"
  - ✅ "2 / 2 records independently verified absent"
- Click: **"Download verification receipt"** to get JSON proof

---

## Model Selection Guide

### For Quick Demos (Recommended)

Use **fast models** to demonstrate flow quickly:

```env
LLM_INVESTIGATOR_MODEL=ollama/phi
LLM_SCOPE_REVIEWER_MODEL=ollama/orca-mini
LLM_JUDGE_MODEL=ollama/phi
LLM_AUDITOR_MODEL=ollama/phi
```

**Speed**: ~2-3 minutes total investigation
**Accuracy**: Good enough to show the workflow

### For Detailed Demos

Use **balanced models** for better reasoning:

```env
LLM_INVESTIGATOR_MODEL=ollama/mistral
LLM_SCOPE_REVIEWER_MODEL=ollama/orca-mini
LLM_JUDGE_MODEL=ollama/mistral
LLM_AUDITOR_MODEL=ollama/phi
```

**Speed**: ~4-5 minutes total investigation
**Accuracy**: Better multi-agent reasoning

### For Best Quality (Patient Audience)

Use **best models** for maximum accuracy:

```env
LLM_INVESTIGATOR_MODEL=ollama/neural-chat
LLM_SCOPE_REVIEWER_MODEL=ollama/mixtral
LLM_JUDGE_MODEL=ollama/neural-chat
LLM_AUDITOR_MODEL=ollama/mistral
```

**Speed**: ~10-15 minutes (mixtral is slower)
**Accuracy**: Excellent reasoning and findings
**Requirement**: 16GB+ RAM

---

## Interactive Scenarios

### Scenario 1: Happy Path (5 minutes)

**Objective**: Show everything working perfectly

1. Give consent (1 min)
2. Investigate (2-3 min)
3. Approve (1 min)
4. Verify deletion (1 min)

**Expected Outcome**: All records deleted, no errors

### Scenario 2: Service Offline (10 minutes)

**Objective**: Show resilience when a service is unavailable

1. Give consent
2. Start investigation
3. Manually stop one service: `lsof -i :8101 | grep -v COMMAND | awk '{print $2}' | xargs kill -9`
4. Investigation continues but marks that service as "unknown"
5. Approval still works (guarded execution)
6. Verification shows: 1 verified absent, 1 unknown

**Expected Outcome**: System handles partial unavailability gracefully

### Scenario 3: Model Comparison (15 minutes)

**Objective**: Compare reasoning quality of different models

1. Run investigation with phi (fast)
   - Note findings and quality
   - Screenshot results
2. Reset demo: `make reset`
3. Switch to mixtral in .env
4. Run investigation again with same data
   - Compare findings
   - Note quality differences

**Expected Outcome**: Larger models catch more edge cases

### Scenario 4: Re-ingestion Prevention (5 minutes)

**Objective**: Show that deleted data can't come back

1. Complete full withdrawal
2. In right panel, click: **"Replay an old search-index job"**
3. System tries to re-add deleted record V1
4. Result: "Re-ingestion blocked. V1 stays absent."

**Expected Outcome**: Safety mechanism prevents accidental re-ingestion

---

## Browser Setup for Demo

### Optimal Layout

Use a wide monitor or arrange windows:

```
┌─────────────────────┬─────────────────────┐
│  Recall Dashboard   │   Any Other App     │
│  (localhost:8501)   │ (8101/8102/8103)    │
│                     │                     │
│  Use for:           │  Use for:           │
│  - Investigate      │  - Show data before │
│  - Approve          │  - Show data after  │
│  - Verify           │  - Verify deletion  │
└─────────────────────┴─────────────────────┘
```

### Browser Tabs Setup

Open these tabs:
1. Recall Dashboard (localhost:8501) — Main
2. Club Portal (localhost:8101) — Reference
3. Class Booking (localhost:8102) — Reference
4. Member Offers (localhost:8103) — Reference

Toggle between them during the demo.

---

## Common Demo Issues & Fixes

### Issue: Investigation Takes Too Long

**Cause**: Using large model (mixtral)

**Fix**: 
```bash
# Edit .env to use smaller models
LLM_INVESTIGATOR_MODEL=ollama/phi
LLM_SCOPE_REVIEWER_MODEL=ollama/orca-mini
```

Then reload browser (F5).

### Issue: Model Not Found

**Cause**: Model not downloaded

**Fix**:
```bash
ollama pull phi
ollama pull orca-mini
# Or use make demo-models to see options
```

### Issue: Service Doesn't Start

**Cause**: Port already in use

**Fix**:
```bash
make kill
sleep 3
make demo
```

### Issue: Data Doesn't Appear in Other Services

**Cause**: Consent not fully processed

**Fix**:
1. Wait 5 seconds after clicking consent
2. Refresh the other service pages (F5)
3. Data should now be visible

---

## Demo Talking Points

### Privacy-First Design
"Notice how the user controls everything. No deletion happens without explicit approval."

### Automated Discovery
"Instead of manually searching for data, LLM agents automatically discover it across services."

### Verified Deletion
"We don't just delete the database—we independently verify each service confirms the data is gone."

### Safety Guards
"Even if an operator makes a mistake, safety checks prevent unintended deletion."

### Multiple Agents
"Different LLM agents review the plan independently, catching errors before execution."

### Actual Deletion
"This isn't a demo—real data is actually being deleted from these real services."

---

## Extending the Demo

### Add More Services

Edit `withdrawal/services.py`:
```python
PORTS = {
    'documents': 8101,
    'search': 8102,
    'personalization': 8103,
    'your_service': 8104,  # Add here
}
```

### Add More Data Types

Edit `data/fitness.json` to include:
- More questionnaire fields
- More derived records
- More dependencies

### Create Custom Scenarios

Edit `demo_scenario.json`:
```json
{
  "user_id": "U1",
  "consent_state": "granted",
  "records": [
    {"id": "D1", "service": "documents", ...},
    ...
  ]
}
```

---

## Advanced: Running Multiple Demos

### Parallel Sessions

You can run multiple parallel demos with different ports:

```bash
# Session 1
RECALL_DATA_DIR=.runtime/demo1 make demo --port 8501

# Session 2 (in another terminal)
RECALL_DATA_DIR=.runtime/demo2 make demo --port 8502
```

### Recording the Demo

```bash
# Use screen capture tool to record:
# macOS: QuickTime Player
# Linux: OBS Studio
# Windows: Snip & Sketch or OBS

# Record while running showcase:
make demo &
make showcase > demo_transcript.txt
```

---

## Feedback & Improvement

After the demo, collect feedback on:
- Is the workflow clear?
- Were the LLM findings helpful?
- Would different models help?
- What features would you add?

---

**Ready to demo?** Run `make demo` and follow along!
