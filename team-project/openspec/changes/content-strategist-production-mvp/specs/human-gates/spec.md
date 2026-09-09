## Purpose

Implements human decision checkpoints in the workflow where users approve, modify, or reject agent outputs before proceeding.

## ADDED Requirements

### Requirement: Strategy approval gate
The system SHALL pause execution after Strategist agent and require explicit user approval before proceeding to Creator agent.

#### Scenario: Strategy approval
- **WHEN** Strategist completes recommendation
- **THEN** system presents recommendation with reasoning and waits for user action (Approve / Modify / Reject)

#### Scenario: Strategy modification
- **WHEN** user selects "Modify"
- **THEN** system accepts user input (new action, format, platform) and routes it back to Strategist for alternative recommendation

#### Scenario: Strategy rejection
- **WHEN** user selects "Reject"
- **THEN** system routes rejection feedback to Strategist, which generates alternative recommendation; user can try again

### Requirement: Final review gate
The system SHALL present generated draft for user review before marking as ready for publishing.

#### Scenario: Final draft review
- **WHEN** Reviewer completes quality assessment
- **THEN** system presents draft with quality scores and waits for user action (Approve / Edit / Rework / Skip)

#### Scenario: User edit capability
- **WHEN** user selects "Edit"
- **THEN** system allows inline editing of draft and routes edited version to Creator for refinement, maintaining voice

#### Scenario: Rework request
- **WHEN** user selects "Rework"
- **THEN** system allows user to specify changes (e.g., "make more technical", "add data") and re-runs Creator agent with revised brief

### Requirement: Decision tracking
The system SHALL log all human decisions (approvals, rejections, modifications) in PostgreSQL for learning and feedback loops.

#### Scenario: Decision logging
- **WHEN** user makes a decision at any gate
- **THEN** system records: gate_type, user_action, timestamp, and any feedback provided

### Requirement: Feedback routing
The system SHALL route user feedback to relevant agents for continuous improvement.

#### Scenario: Feedback incorporation
- **WHEN** user provides feedback (e.g., "too generic", "wrong format")
- **THEN** system routes it to appropriate agent (Creator or Strategist) for next attempt
