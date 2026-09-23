# Evaluation and limits

## Success criterion

Target: at least 9 of 10 **completable controlled live trials** finish within three minutes of request submission through reviewed, approved, verified withdrawal, preserve the paid booking and unrelated records, and make no unauthorized writes. The manual baseline has not been timed. Correct handling of an outage, denied approval, or ambiguity is scored separately; it is not a successful full withdrawal.

A three-minute video edit is not evidence of a three-minute execution. The test scripts use explicit scripted approval restricted to expected synthetic targets; a real user still approves through the UI.

## Reproduce

From `week3/`:

```bash
make test
# Optional real browser check:
.venv/bin/python -m pip install -r requirements-browser.txt
.venv/bin/python -m playwright install chromium
make test-browser
# Optional MCP transport test dependency:
make install-mcp
```

Tests use temporary stores. Fixed-port launcher checks can skip when the running demo occupies those ports. MCP round-trip checks skip if the optional SDK is absent. Mocked model tests verify control flow and evidence contracts, not live reasoning quality.

To run a paid live evaluation deliberately:

```bash
.venv/bin/python scripts/evaluate_live.py --live --trials 1
# For the proposed repeated healthy-fixture target:
.venv/bin/python scripts/evaluate_live.py --live --trials 10 --output docs/audit/live-ten-trials.json
```

The runner starts three temporary HTTP stores, gives synthetic consent, deletes only the source, invokes the configured live investigator/reviewer/judge, permits scripted approval only for the predeclared seven-record closure, executes, and calls the live outcome auditor. It never resets or operates on the running demo's data. Even ten successes on this one fixture would not establish real-world generalization; vary wording and use held-out graphs separately.

## LangGraph migration validation — 2026-09-23

- Full regression: **48 Python tests and 24 JavaScript tests passed**, including optional MCP round trips, approval boundaries, repair limits, interrupted execution recovery, and corrected auditor evidence.
- [Isolated live LangGraph trial](audit/langgraph-live-evaluation.json): **12.84 seconds**, complete, six preparation model calls plus the outcome audit, all seven targets absent, B1/D2/V3 preserved. The auditor accurately identifies removed versus retained records. Approval was scripted for the exact synthetic scope; existing demo stores were not reset.
- Pitch outputs: five slides in HTML/PDF; HTML narration matches the 300-word speaker script. PowerPoint output was subsequently removed to keep only the requested formats.
- One successful trial does not establish the proposed 9/10 reliability target. The archived evaluation below predates migration.

## Evidence from the earlier audit

- [Connected live evaluation](audit/live-evaluation.json): one complete live-model trial finished in **10.17 seconds**, with the expected seven-record scope, preserved records, scoped writes, and passing service behavior checks. Approval was scripted for this isolated test. **1/1 is a smoke test, not evidence of 9/10 reliability.**
- Python checks cover approval gates, lineage/version changes, real HTTP service outages, interruption recovery, protected records, notification deduplication, provider calls, misleading clarification correction, replacement-preview invalidation and the dashboard workflow.
- JavaScript checks cover ten golden scenarios plus consent, sharing, source-only deletion, approval, retries, lost responses, reload recovery and suppression. G09's dataset row is supplemented by a separate mocked-investigator ambiguity test; the suite is not a ten-case live-agent benchmark.
- `tests/embedded_apps.py` exercises consent → source deletion → approval → verified removal → reset in Chromium, including the protected booking, no JavaScript errors and a 390px mobile layout.
- [Public observation](audit/public-observation.json) records read-only HTTP/browser observations separately from source/staged/public asset equality. Public availability does not establish local-backend deployment.

Final command results and skips are recorded in [audit summary](audit/validation.json). Any missing evidence or failed check must remain visible; do not rewrite the answer key to make an evaluation pass.

## Findings fixed during the audit

1. An unused legacy judge could default to approval on malformed prose; the unused API was removed. Active review continues to require valid structured, referenced evidence.
2. A new failed investigation could leave a prior preview approvable after reload; replacement attempts now persistently invalidate the old preview.
3. An unresolved outcome auditor could set status to partial but leave a true full-completion flag; both values now agree.
4. A browser test used stale broad selectors after the UI acquired multiple cards; it now checks the intended headings and navigation explicitly.
5. Documentation overstated SMTP support, Flask routes, memory behavior, deployment topology and prior test results; maintained references now describe the implementation.

## Not established

The 90% live success target, production multi-user security, real external queue cancellation/delivery, legal compliance, backup removal and model unlearning. The public browser implementation has one investigator and simulated stores; it has no model judge/outcome auditor or independent backend services. Optional MCP must be tested with its dependency installed before presenting that transport as verified in a particular environment.
