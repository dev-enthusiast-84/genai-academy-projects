## Purpose

Generates high-quality draft content in the user's voice based on approved strategy and historical voice samples.

## ADDED Requirements

### Requirement: Voice-consistent content generation
The system SHALL generate draft content that matches the user's established voice and style by incorporating historical voice samples into the generation prompt.

#### Scenario: Voice sample integration
- **WHEN** Creator agent generates a draft
- **THEN** it retrieves 3-5 voice samples from PostgreSQL and includes them in the generation prompt to establish tone/style

#### Scenario: Consistent tone output
- **WHEN** user has established voice as "technical but accessible"
- **THEN** generated drafts maintain that tone across different content types

### Requirement: Format-specific content generation
The system SHALL generate content appropriate to the target format (short post, blog article, thread, etc.) with format-specific conventions.

#### Scenario: Blog post generation
- **WHEN** the approved brief specifies format as "blog_post"
- **THEN** generated content includes title, structured sections, and blog-appropriate length (800-2000 words)

#### Scenario: LinkedIn thread generation
- **WHEN** format is "linkedin_thread"
- **THEN** generated content is split into numbered tweets with hooklines and conclusions

### Requirement: Structured output with metadata
The system SHALL return generated drafts with metadata (word count, reading time, quality metrics).

#### Scenario: Draft with metadata
- **WHEN** draft is generated
- **THEN** output includes: title, body, word count, reading time minutes, quality scores

### Requirement: Revision loop support
The system SHALL accept revision requests and regenerate drafts based on user feedback.

#### Scenario: User-requested revision
- **WHEN** user requests changes (e.g., "make it more concise")
- **THEN** Creator regenerates with revised instructions, maintaining voice consistency
