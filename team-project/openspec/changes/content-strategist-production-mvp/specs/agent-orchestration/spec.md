## Purpose

Coordinates multi-agent execution with state management, enabling sequential agent workflows with human decision points and feedback routing.

## ADDED Requirements

### Requirement: State machine orchestration
The system SHALL use LangGraph to define a state machine that coordinates the execution of multiple agents with defined state transitions.

#### Scenario: Basic workflow execution
- **WHEN** a user submits content for processing
- **THEN** the system transitions through Strategist → Creator → Reviewer agents in sequence, maintaining state between transitions

#### Scenario: Human gate enforcement
- **WHEN** a human gate is reached (after Strategist or Reviewer)
- **THEN** the system pauses execution and awaits user approval/modification before proceeding to next agent

### Requirement: Feedback routing
The system SHALL route user feedback (approvals, rejections, modifications) back to relevant agents for revision or rework.

#### Scenario: Strategy rejection
- **WHEN** user rejects a Strategist recommendation
- **THEN** the system routes the rejection feedback to Strategist, which generates an alternative recommendation

#### Scenario: Draft revision loop
- **WHEN** user requests edits to a generated draft
- **THEN** the system routes revised instructions to Creator agent and re-runs it

### Requirement: Error handling and recovery
The system SHALL gracefully handle agent failures and provide clear error states without losing workflow context.

#### Scenario: LLM API timeout
- **WHEN** an agent call times out (>30 seconds)
- **THEN** the system logs the error, returns a user-facing error message, and allows retry from the same state

#### Scenario: Malformed agent output
- **WHEN** an agent returns unparseable output
- **THEN** the system detects the parse error, logs it, and prompts user with fallback guidance
