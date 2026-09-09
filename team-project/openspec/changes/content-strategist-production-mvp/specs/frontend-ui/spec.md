## Purpose

Defines the frontend user interface components, layout, and interaction flows for the MVP web application.

## ADDED Requirements

### Requirement: Workflow stage UI
The system SHALL display different UI components based on current workflow stage.

#### Scenario: Input stage
- **WHEN** user loads application
- **THEN** system displays input form: textarea for content + source selector dropdown
- **AND** "ANALYZE CONTENT" button is disabled until text entered

#### Scenario: Strategy gate stage
- **WHEN** Strategist agent completes
- **THEN** system displays recommendation card with:
  - Action badge (color-coded: Publish/Repurpose/Rework/Combine/Skip)
  - Confidence score as progress bar (e.g., "87%")
  - Reasoning explanation text
  - Top 5 similar posts with engagement metrics
  - Approval controls: [APPROVE] [REJECT] [MODIFY TEXT INPUT]

#### Scenario: Creator stage
- **WHEN** strategy approved and Creator agent starts
- **THEN** system displays loading spinner: "Generating draft in your voice..."

#### Scenario: Final review stage
- **WHEN** Reviewer agent completes
- **THEN** system displays final draft card with:
  - Quality score (star rating or numerical: 4.2/5.0)
  - Quality notes (checkmarks: "Clear & concise", "No generic phrases")
  - Full generated draft text (editable in textarea)
  - Approval controls: [APPROVE FOR PUBLISH] [REVISE DRAFT] [START OVER] [COPY TO CLIPBOARD]

### Requirement: Responsive layout
The system SHALL adapt UI to different screen sizes.

#### Scenario: Desktop layout (≥1024px)
- **GIVEN** desktop or tablet screen
- **THEN** sidebar on left (navigation, status), main content on right
- **AND** cards display in full width with proper spacing

#### Scenario: Mobile layout (<1024px)
- **GIVEN** mobile screen
- **THEN** no sidebar, full-width content
- **AND** navigation becomes hamburger menu
- **AND** cards stack vertically

### Requirement: Visual feedback and state management
The system SHALL provide clear visual feedback during workflow execution.

#### Scenario: Loading states
- **WHEN** agent is processing
- **THEN** show animated spinner with stage name: "Analyzing content..." / "Generating draft..." / "Checking quality..."
- **AND** disable approval buttons until processing complete
- **AND** show elapsed time if processing takes >5 seconds

#### Scenario: Error states
- **WHEN** agent fails or times out
- **THEN** display error card with user-friendly message: "Analysis took too long, please try again"
- **AND** show [RETRY] button to restart from current stage
- **AND** link to observability dashboard (LangSmith trace) for debugging

#### Scenario: Success confirmation
- **WHEN** user approves and workflow completes
- **THEN** display success message: "Draft approved! Ready to publish"
- **AND** show [COPY] and [DOWNLOAD] options
- **AND** show [START NEW ANALYSIS] button to begin new workflow

## IMPLEMENTATION DETAIL: Component Architecture

### Component Hierarchy
```
<WorkflowApp>
  ├─ <Header />
  │  ├─ Title: "Content Strategist"
  │  ├─ Theme Toggle
  │  └─ Help Link
  ├─ <MainLayout>
  │  ├─ <Sidebar /> (desktop only)
  │  │  ├─ Navigation
  │  │  ├─ Current Stage Badge
  │  │  └─ Workflow Progress: ██░░░░░░ 30%
  │  └─ <ContentArea>
  │     ├─ <StageRouter /> (renders based on currentStage)
  │     │  ├─ <InputStage />
  │     │  ├─ <StrategyGateStage />
  │     │  ├─ <CreatorLoadingStage />
  │     │  ├─ <ReviewerLoadingStage />
  │     │  └─ <FinalReviewStage />
  │     └─ <ErrorBoundary />
  └─ <Footer />
     └─ Links: GitHub | LangSmith Traces | Docs
```

### Key Components

**InputStage**
```
Input Your Content
──────────────────
[TEXTAREA: "Paste webinar notes, blog outline, or content idea..."]

Source: [DROPDOWN: "Webinar Notes" / "Paste / "LinkedIn Auto" (phase 2)]

[ANALYZE CONTENT BUTTON]
```

**RecommendationCard (StrategyGateStage)**
```
📋 Strategist Recommendation
────────────────────────────
Action: [🟢 REPURPOSE] Confidence: ████████░ 87%

"Your content matches successful technical deep-dives. 
Recommend repurposing as a LinkedIn thread with 5-7 parts 
plus a blog post version."

Similar High-Performing Posts:
┌─────────────────────────────┐
│ "AI in Product Development" │
│ 2.1K impressions | 14% eng   │
└─────────────────────────────┘
(... 4 more items)

[APPROVE] [REJECT] [MODIFY: text input box]
```

**DraftCard (FinalReviewStage)**
```
✍️ Generated Draft
──────────────────
Quality Score: ★★★★☆ 4.2/5.0

Quality Notes:
✓ Clear writing, good structure
✓ Tone consistent with voice samples
⚠ Consider removing: "In today's world..."

────────────────────────────
Your generated draft is ready:
[TEXTAREA: full draft text, editable]
────────────────────────────

[APPROVE FOR PUBLISH] [REVISE DRAFT] [START OVER] [COPY]
```

### State Management (React Query Pattern)
```typescript
// Workflow state hook
const useWorkflowState = () => {
  const { data: state } = useQuery('workflow-state', 
    () => fetch('/api/workflow/state').then(r => r.json())
  );
  return state;
};

// Gate approval mutation
const useApproveStrategy = () => {
  return useMutation((recommendation) => 
    fetch('/api/workflow/gate/strategy-approve', {
      method: 'POST',
      body: JSON.stringify(recommendation)
    })
  );
};
```

## IMPLEMENTATION DETAIL: Colors and Styling

### Action Badge Colors
- Publish: 🟢 Green (#059669)
- Repurpose: 🔵 Blue (#2563eb)
- Rework: 🟡 Amber (#d97706)
- Combine: 🟣 Purple (#7c3aed)
- Skip: ⚪ Gray (#64748b)

### Status Colors
- Success: Green (#059669)
- Warning: Amber (#d97706)
- Error: Red (#dc2626)
- Info: Blue (#2563eb)

### Spacing and Typography
- Font: System font stack (-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif)
- Card padding: 1.5rem
- Border radius: 8px
- Line height: 1.6

## Phase 2: Enhanced UI

- Multi-user workspaces with team collaboration
- Draft history and version comparison
- Performance analytics dashboard
- Direct publish to LinkedIn/Twitter/Substack (from UI)
- Workflow customization UI (user-defined gates and parameters)
