# Week 3 submission document draft

Copy this reviewed material into the required Google Doc; this Markdown file is not a submitted Google Doc.

## Project overview

**Recall — consent has an undo button.** Recall helps fitness-club members withdraw personalization consent and remove linked questionnaire copies through a privacy dashboard, replacing manual requests and removal checks across three apps; it autonomously investigates with three read tools, coordinates reviewed and human-approved removal and verification, hands off when intent or evidence is unclear and before deletion, and targets verified removal with the paid booking preserved in under three minutes in at least 9 of 10 completable controlled live trials.

Bring-your-own use case, code-heavy track: LangGraph orchestration, a bounded Python tool loop, and a SQLite state machine. The system demonstrates model-selected reads, multi-role review, bounded repair, persisted human approval, guarded writes, recovery and independent verification. [Framework answers](FRAMEWORK.md) map every questionnaire field to this implementation.

## Datasets

`data/fitness.json` contains fictional fitness-club records, explicit lineage, a protected paid booking, unrelated records and another synthetic user. `site/fitness.json` is the browser scenario fixture; `data/golden/fixtures.json` and `cases.json` provide ten controlled boundary/failure scenarios. No customer dataset, scraped personal data or vector store is used; see [evaluation](EVALUATION.md) for evidence and limits.

## AI coding prompts and iterations

The following are paraphrases of requests in this development session, not invented verbatim transcripts:

- Move the receipt and approval out of a narrow right column into available page space.
- Fix unreadable download/approval button colors and hover behavior.
- Remove local model integrations and their infrastructure commands.
- Give refresh actions visible feedback and remove repeated onboarding instructions.
- Correct investigation that confused a queued invitation with the protected paid booking or mistook descendants for shared dependencies.
- Show human-readable record/app names, with machine IDs available only as technical mappings.
- Audit the implementation, hosted app, scripts and documentation against the Week 3 handout.

Codex inspected source and fixtures, edited code, added targeted regressions, ran tests and made isolated live-model checks. Model-authored clarifications initially blocked valid plans; evidence-guided bounded correction and explicit type/lineage context were added. Deterministic checks and human approval remained mandatory throughout.

## Observations and learnings

A passing unit test does not establish live model quality: a real investigator confused record types and another search used unsupported structured syntax. Explicit evidence, bounded retries and honest clarification are necessary. Consent withdrawal, removal, service-side blocking and verification are separate states; an unavailable app must remain unresolved. Separate copied deployment assets also drifted from source, so a checked sync step was added.

The archived evaluation records one complete controlled live trial with scripted approval. It predates the LangGraph migration and does not establish the 9/10 target; the separate LangGraph migration smoke trial also completed successfully in 12.84 seconds with exact scripted approval (see Evaluation). The public browser version is a one-investigator simulation, not the multi-role local backend.

## Links and remaining submission work

- Code: https://github.com/dev-enthusiast-84/genai-academy-projects/tree/main/week3
- Public browser demonstration: https://dev-enthusiast-84.github.io/genai-academy-projects/recall/
- Google Doc URL: **not yet supplied/created in this audit**
- Video URL (five minutes or less): **not yet supplied/recorded in this audit**
- Final form submission: **not performed**

Use [three-minute demo script](demo-script-3-min.md), [evaluation](EVALUATION.md) to finish the submission without overstating results. The handout lists August 30, 2026 for Builder of the Week and September 16, 2026 for certification; the audit does not verify form availability or acceptances.
