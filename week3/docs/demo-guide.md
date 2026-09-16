# Demo guide

Start the four apps with `make demo`, then open them with `make open-all`. Configure OpenAI or OpenRouter in `.env` or the Recall sidebar. Use **Guided rehearsal** if you want a scripted run without model calls.

## Show the problem

1. In Club Portal, give consent and share fitness interests.
2. Inspect personalized recommendations in Class Booking and the queued offer in Member Offers.
3. Delete only the questionnaire in Club Portal. The downstream records remain and sharing consent is still active.

## Withdraw consent

1. In Recall, ask to withdraw fitness-personalization consent for questionnaire D1 while preserving the paid booking.
2. Prepare the plan. Live mode investigates recorded lineage, reviews scope, and evaluates the proposal with a separate judge model.
3. Review the exact records and the findings. Preparation does not delete data.
4. Tick the approval checkbox and select **Approve & withdraw**.
5. Inspect the receipt, independent verification, customer experience checks, and execution timeline.

## Verify the result

Refresh each customer app. Personalized copies should be removed, their stable IDs blocked from re-ingestion, and the paid booking preserved. Download the receipt to inspect the recorded outcome.

## Recovery scenarios

The sidebar supports offline services, temporary failures, a lost delete response, and interruption after one deletion. Inspect partial results and use **Restore demo services & resume**. Approval has a bounded retry allowance and expires after 24 hours; a new scope requires new approval.

`make restart` preserves state. `make reset` clears the synthetic data and history for a fresh demonstration. `make test` checks workflows without live model calls.

See [Configuration](configuration.md) and [Troubleshooting](troubleshooting.md).
