## Purpose

Validates generated content for quality, tone consistency, clarity, and brand alignment before final user review.

## ADDED Requirements

### Requirement: Quality assessment
The system SHALL evaluate generated drafts across multiple dimensions: tone consistency, clarity, readability, and generic phrase detection.

#### Scenario: Quality scoring
- **WHEN** Reviewer analyzes a draft
- **THEN** it returns scores for: tone_consistency (0-1), readability (0-10), generic_phrase_count, and flags problematic phrases

#### Scenario: Generic content detection
- **WHEN** draft contains overused AI phrases (e.g., "in today's world", "it's important to note")
- **THEN** Reviewer flags them with location and suggests alternatives

### Requirement: Tone consistency validation
The system SHALL compare draft tone against user's voice profile and flag inconsistencies.

#### Scenario: Tone mismatch detection
- **WHEN** user voice profile indicates "technical and direct" but draft is "casual and conversational"
- **THEN** Reviewer flags the mismatch and suggests adjustments

#### Scenario: Tone consistency pass
- **WHEN** draft maintains consistent tone with voice samples
- **THEN** Reviewer flags no tone issues and includes positive validation

### Requirement: Structured quality output
The system SHALL return quality assessments with actionable feedback rather than pass/fail verdicts.

#### Scenario: Quality report with feedback
- **WHEN** Reviewer completes assessment
- **THEN** it returns: quality_score, tone_consistency_score, readability_score, list of issues (with locations), and suggested improvements

### Requirement: Escalation for low-quality drafts
The system SHALL flag drafts below quality threshold (score <6/10) for user review with detailed feedback.

#### Scenario: Low quality escalation
- **WHEN** draft quality score is below 6/10
- **THEN** Reviewer marks for escalation and provides detailed reasons (e.g., "generic opening, unclear CTA, misaligned tone")
