## Purpose

Accepts user-submitted content (webinar notes, ideas, drafts) via text input, analyzes them using golden dataset context, and runs through full agentic workflow (MVP) with future support for rich file formats.

## ADDED Requirements

### Requirement: Text-based content ingestion (MVP)
The system SHALL accept content via direct text input (paste or plain text files) for MVP simplicity.

#### Scenario: Text paste ingestion
- **WHEN** user pastes content into the input form
- **THEN** system accepts it, stores in PostgreSQL with timestamp and content type

#### Scenario: Plain text file upload
- **WHEN** user uploads .txt file
- **THEN** system parses file and stores content in PostgreSQL

#### Scenario: Content type tagging
- **WHEN** content is ingested
- **THEN** user can tag it as: webinar_notes, draft_idea, inspiration, or other for context

### Requirement: Content analysis using golden dataset
The system SHALL analyze submitted content against golden dataset to identify opportunities and patterns.

#### Scenario: Semantic matching
- **WHEN** user submits content
- **THEN** system embeds it, queries Pinecone for similar golden posts, and identifies performance patterns to inform strategy

#### Scenario: Opportunity identification
- **WHEN** analysis completes
- **THEN** system notes: suggested content angles, recommended formats, and expected performance based on golden data

### Requirement: Full agentic workflow execution
The system SHALL route analyzed content through complete workflow: Strategist → human gate → Creator → Reviewer → final gate.

#### Scenario: End-to-end workflow
- **WHEN** user submits content
- **THEN** system automatically runs: Content Ingest → Strategist recommendation → user approval → Creator draft → Reviewer check → final approval

#### Scenario: Decision-based routing
- **WHEN** user approves at strategy gate
- **THEN** system proceeds to Creator; when user rejects, system offers alternative recommendations

### Requirement: Format selection and generation
The system SHALL support generating content in multiple formats (LinkedIn post, blog article, thread) based on Strategist recommendation.

#### Scenario: Format-specific generation
- **WHEN** user approves recommendation with suggested format
- **THEN** Creator generates content in that specific format (e.g., LinkedIn thread with numbered tweets)

#### Scenario: Format alternatives
- **WHEN** recommendation suggests multiple formats
- **THEN** user can select which format to generate (can generate multiple sequentially)

### Requirement: Iteration and feedback
The system SHALL allow users to iterate within workflow session without losing context.

#### Scenario: Recommendation rejection
- **WHEN** user rejects Strategist recommendation
- **THEN** system offers to generate alternative without resetting state

#### Scenario: Draft revision
- **WHEN** user requests draft changes
- **THEN** system accepts revision instructions and re-runs Creator, maintaining voice and context

## PHASE 2: Rich File Format Support (Future Improvement)

### Requirement: PDF and DOCX parsing
The system SHALL support PDF, DOCX, and Markdown file uploads with text extraction.

#### Scenario: PDF upload and parsing
- **WHEN** user uploads PDF file
- **THEN** system extracts text using pypdf library and processes through ingestion pipeline

#### Scenario: DOCX support
- **WHEN** user uploads .docx file
- **THEN** system extracts text content and metadata using python-docx library

#### Scenario: Format-preserving extraction
- **WHEN** files are parsed
- **THEN** system preserves important structure (headers, sections, lists) while extracting clean text

### Requirement: Advanced content analysis (Phase 2)
The system SHALL automatically extract topics, themes, and angles from uploaded content.

#### Scenario: Topic and angle extraction
- **WHEN** complex document is uploaded
- **THEN** system automatically identifies: main topics, potential angles, key takeaways, and suggests content opportunities

#### Scenario: Multi-angle support
- **WHEN** content contains multiple distinct ideas
- **THEN** system can generate recommendations for multiple angles simultaneously
