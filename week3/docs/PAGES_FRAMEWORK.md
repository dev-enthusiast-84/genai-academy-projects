# Recall — hosted demo framework

## One-liner

Recall helps fitness-club members withdraw shared questionnaire information through a privacy dashboard, replacing manual requests to each connected app. It uses five tools to investigate the trail, execute approved removals, and verify the result; it asks before writes or when scope is unclear. Target: correctly handle 9 of 10 controlled workflows in under three minutes, with zero unauthorized deletions and the paid booking preserved.

The target is not a measured live-model result. Correctly reporting an outage does not count as successful full withdrawal.

| Field | Answer |
| --- | --- |
| Goal | Withdraw the selected sharing consent and linked information, then verify the outcome. |
| Surface | Recall is a separate browser app alongside Club Portal, Class Booking, and Member Offers. |
| Steps | Consent → automatic sharing → source-only deletion → investigate → clarify or propose → approve → remove → verify. |
| Tools | Discover, trace, inspect, and verify are reads; approved deletion is a write. The model only receives the investigative read tools. |
| Memory | Credentials and conversation stay in memory. Request state persists in this browser for 24 hours; provenance and withdrawal markers remain until reset. |
| Hard limits | No unapproved deletion, cross-user access, guessed lineage, protected-booking deletion, or false completion. |
| Human review | Approve exact records, consent withdrawal, and ingestion blocks; changed scope requires a new plan. |
| Failure handling | Bound retries, inspect uncertain writes, save unfinished work, and report inaccessible records as unknown. |
| Success | Correct end-to-end outcomes, no unauthorized actions, preserved booking, and accurate unresolved results. Measure full withdrawals separately. |

The hosted build uses a live model investigator and deterministic execution guards. Its customer pages have separate simulated service records in browser storage; they are not independently hosted backends. The connected Python implementation is a separate local deployment with additional review stages. No model key is published.
