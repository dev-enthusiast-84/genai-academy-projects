## Purpose

Demonstrates workflow for tracking published LinkedIn posts and using their performance history to inform future recommendations via golden dataset (MVP) with path to real API integration.

## ADDED Requirements

### Requirement: Golden dataset initialization (MVP)
The system SHALL seed PostgreSQL with realistic historical LinkedIn posts and engagement metrics for demo purposes.

#### Scenario: Golden dataset loading
- **WHEN** system initializes
- **THEN** it loads 15 pre-seeded LinkedIn posts with realistic engagement data (impressions, reactions, comments, etc.)

#### Scenario: Performance memory population
- **WHEN** golden posts are loaded
- **THEN** system embeds them, stores in Pinecone, making them available for similarity search

#### Scenario: Demo content selection
- **WHEN** user selects "Try with demo data"
- **THEN** system presents 3 demo scenarios for testing (technical post, opinion piece, personal story)

### Requirement: Post ingestion interface (MVP)
The system SHALL allow users to manually add posts to workflow for processing.

#### Scenario: Manual post submission
- **WHEN** user pastes LinkedIn post text or provides content
- **THEN** system accepts it, stores in PostgreSQL, and runs through agentic workflow using golden dataset context

#### Scenario: Workflow integration
- **WHEN** post is submitted
- **THEN** Strategist analyzes it against golden dataset posts (via Pinecone semantic search) and provides recommendations

### Requirement: Performance memory learning (MVP)
The system SHALL demonstrate memory-driven recommendations using golden dataset.

#### Scenario: Pattern recognition from golden data
- **WHEN** Strategist analyzes new content
- **THEN** it queries Pinecone for similar golden posts and uses their engagement data to inform recommendations

#### Scenario: Accuracy demonstration
- **WHEN** golden dataset is used
- **THEN** recommendations are based on actual performance patterns (e.g., "technical posts average 15% engagement")

## PHASE 2: Real LinkedIn Integration (Future Improvement)

### Requirement: LinkedIn API integration
The system SHALL connect to LinkedIn API to automatically detect and import published posts.

#### Scenario: API-driven post detection
- **WHEN** LinkedIn API is configured
- **THEN** system polls API every 1 hour to detect newly published posts and automatically ingests them

#### Scenario: Real performance tracking
- **WHEN** posts are published
- **THEN** system continuously collects real engagement metrics from LinkedIn API (impressions, reactions, comments, shares)

#### Scenario: Memory refinement with real data
- **WHEN** real posts accumulate engagement data
- **THEN** system embeds them, adds to Pinecone, replacing/augmenting golden dataset with user's actual performance history

### Requirement: Automatic memory update
The system SHALL continuously improve recommendations as real engagement data accumulates.

#### Scenario: Real-time learning
- **WHEN** user publishes more content over time
- **THEN** Strategist recommendations become increasingly personalized based on their actual performance patterns (no longer relying on golden dataset)
