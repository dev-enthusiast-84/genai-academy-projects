# Workflow recovery

The current fitness-consent proposal and dashboard workflow view are retained. Recovery restores the behavior behind that view; it does not replace the project proposal.

## Restored behavior

- Three independent HTTP applications with separate SQLite stores; consent in Club Portal shares the profile with Class Booking and Member Offers.
- Deleting the source profile leaves downstream copies visible, demonstrating the problem.
- Bounded model investigation, scope review, and a judge prepare an exact plan. Human approval is required before withdrawal.
- Saved approval and progress, bounded retries, outage recovery, independent absence checks, protected bookings, and replay blocking.
- Optional read-only MCP transport and configurable OpenAI/OpenRouter models remain available.

## Current UI retained

The withdrawal journey, privacy steps, action buttons, sharing diagram, connected-app links, model selectors, evidence trail, and receipt remain in `app.py`. Customer applications use `ui/customer.css`; Recall uses `ui/recall.css`.

## Run

Stop the previous demo using Ctrl+C in its terminal, then run `./demo.sh`. The launcher starts Recall on port 8501 and the customer apps on 8101–8103. Model calls use the existing `.env`; guided rehearsal requires no model call. Use `--reset` only when intentionally resetting synthetic data.

## Verification

- Python: 21 passing tests, including the complete dashboard workflow, fresh-session recovery, actual service outage, approval boundaries, and protected booking.
- Two checks skipped: optional MCP SDK integration (SDK absent), and fixed-port launcher smoke test (existing demo occupied the ports).
- Browser engine: 23 passing tests. Customer pages checked at desktop and 390px width.
- Live model quality and the handout's timed success-rate target have not been measured in this recovery pass.

Pre-recovery source copies are retained locally in `.runtime/recovery-backup/`. Existing JSON runtime files were not deleted; the recovered workflow uses SQLite stores.
