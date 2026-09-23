# Recall — Avery’s three-minute app demo

Use the **local connected apps with Live agent mode**. This walkthrough follows the [pitch deck](pitch/recall-pitch.html): meet Avery → see sharing → discover surviving copies → approve a precise withdrawal → prove removal, preservation, and blocked reuse. The deck’s two-minute talk is separate from this demo.

**Presentation budget: three minutes, including navigation.** Model latency varies; rehearse first. For a recorded demo, shorten only model-processing waits and label those cuts **“Model processing wait shortened.”** Keep the real request, progress, returned findings, approval, and result visible. An unedited live run may take longer.

## Set up before recording

1. Start the local apps with `make demo` if they are not already running. Open four tabs in this order; use these existing tabs throughout:

   | Tab | App and matching deck indicator | Address |
   |---|---|---|
   | 1 | Club Portal · rust membership-card icon | http://127.0.0.1:8101 |
   | 2 | Class Booking · green calendar icon | http://127.0.0.1:8102 |
   | 3 | Member Offers · plum invitation icon | http://127.0.0.1:8103 |
   | 4 | Recall · gold undo icon | http://127.0.0.1:8501 |

2. In Recall, open **Settings & reset** at the upper left. Check the configured provider and four model roles. The **LLM judge model** must differ from the investigator model. Use **Load available models** if needed. Keep credentials off camera. `make demo-models` prints model selections without keys.
3. Under **Demo controls**, select **Investigation mode → Live agent**, then **Execution scenario → Healthy services**. Tick **Reset all local synthetic data and request history** and click **Reset demo**. This clears earlier synthetic requests and withdrawal blocks; download any receipt you want to retain first. Confirm the reset success message and the selected mode.
4. Refresh all three customer tabs. Club Portal must offer **Give consent & share interests**. Class Booking must show **Your confirmed Saturday strength class**, without the yoga recommendation. Member Offers must have no personalized invitation. Leave Class Booking’s search empty throughout.
5. Rehearse with the actual configured models, including the outcome audit. Then reset and refresh again. Start the recording in Club Portal with Avery’s persona and consent controls in view. Collapse Recall’s sidebar after briefly showing **Live agent** during the demo.

Use this request, which matches the app’s default:

> Withdraw my fitness-personalization consent for my fitness interests questionnaire. Remove its shared interests, recommendations and queued offers. Keep my paid class booking.

## Screen-by-screen script

The quoted lines are conversational prompts. Point at the relevant evidence while speaking; do not read every record or review finding.

### 0:00–0:18 · Club Portal — introduce Avery and share

**Navigate and act:** Tab 1. Point to the same Avery illustration used in the deck: **Avery Example**, evening yoga after 6 pm, paid Saturday strength class. Tick **I consent to share this profile…** and click **Give consent & share interests**. Show **Sharing consent active**.

> “Meet Avery, our fictional club member. They like evening yoga and already have a paid Saturday class. In Club Portal, they agree to share their interests with two apps. Watch what that one choice creates.”

### 0:18–0:38 · Class Booking, then Member Offers — show the benefit

**Navigate and act:** Tab 2 → **Refresh this app**. Show **Recommended for you: evening yoga** beside **Your confirmed Saturday strength class**. Tab 3 → **Refresh this app**. Show **Your evening yoga invitation**. Use the green calendar and plum invitation icons to connect these screens to the deck.

> “Class Booking recommends yoga, while keeping the paid booking separate. Member Offers prepares a yoga invitation. This is a local preview; nothing is sent. So far, the sharing is useful.”

### 0:38–0:55 · Club Portal, then both downstream apps — expose the gap

**Navigate and act:** Tab 1 → **Delete questionnaire only**. Show **Questionnaire removed · consent still active**. Refresh tabs 2 and 3: the yoga recommendation and invitation remain.

> “Now Avery changes their mind. Deleting the questionnaire removes the original, but these apps still hold copies. Avery wants personalization stopped without losing the class they paid for.”

### 0:55–1:25 · Recall — ask the agents to investigate

**Navigate and act:** Tab 4 → reload the page so Recall sees the external changes. Briefly show **Live agent** in the sidebar, then collapse it. Click **Manage consent withdrawal ↓**. Keep the prepared request in **What would you like withdrawn?** and click **Prepare withdrawal plan**. Show the tool and review progress while real model calls run.

> “Recall is Avery’s privacy dashboard. I ask it to remove personalization and keep the booking. The investigator chooses read tools and follows recorded relationships. LangGraph coordinates the scope reviewer, a separate judge, and bounded repairs. That helps turn a human request into a checked plan.”

### 1:25–1:45 · Recall receipt — inspect scope and approve

**Navigate and act:** Show **Live model investigation** and **Evaluation: pass**. Expand **Review findings and corrections**, point to one actual finding, then collapse it. At **Review the exact change**, show the seven targets and the preservation note. Point out **Already absent** beside the questionnaire: its action is **Recheck absence and block re-import**; the six remaining records show **Still stored**. Tick **I approve these deletions and re-ingestion blocks**; click **Approve & withdraw**.

> “Here are the model reviews and the exact scope: seven targets, including the questionnaire already deleted. The booking and membership stay. Models propose; Avery approves. Code checks ownership, versions, and that exact approval before any withdrawal writes.”

### 1:45–2:10 · Recall receipt — verify and explain the architecture

**Navigate and act:** Wait for **WITHDRAWAL VERIFIED** and **7 / 7**. Show **Customer experience checks**, especially **Paid class booking preserved — pass**, and the actual **Outcome auditor findings**. Briefly scroll to **Execution timeline** to show recorded approval, work, and verification.

> “Independent service reads verify all seven targets are absent. The third agent—the outcome auditor—reviews those results. SQLite saves approval and progress so interrupted work can resume. Language models interpret and review; the durable workflow keeps execution controlled and gives us evidence.”

### 2:10–2:38 · All three customer apps — prove Avery’s outcome

**Navigate and act:** Tab 1 → refresh: **Sharing consent withdrawn**; membership contact remains. Tab 2 → **Refresh this app** with an empty search: the yoga recommendation is gone, **Your confirmed Saturday strength class** remains, and public classes are still available. Tab 3 → refresh: **No shared personalization records are stored here**, **0 visible items**, no yoga invitation.

> “Let’s check the apps themselves. Sharing is withdrawn. The recommendation and invitation disappear. Avery’s membership and paid Saturday strength class remain. This is a precise privacy change that preserves the service Avery still wants.”

### 2:38–3:00 · Recall — stop old copies returning and keep the proof

**Navigate and act:** Tab 4 → completed receipt → **Replay an old search-index job**. Show **Re-ingestion blocked. V1 stays absent.** Click **Download verification receipt**. End on the verified result.

> “What if an old job brings the preference back? This replay is blocked. We can download the receipt showing what changed. Avery can change their privacy choice, keep the paid booking, and see evidence that the connected apps respected the request.”

## Data checkpoints — match the deck, not an old session

The local fixture [data/fitness.json](../data/fitness.json) and browser fixture [site/fitness.json](../site/fitness.json) contain identical story data. These are expected states of the **connected local apps** as the walkthrough progresses:

| Story beat | Records and visible result |
|---|---|
| Fresh reset | Consent not granted; no shared yoga records. B1 paid Saturday strength class at **10 am**, D2 membership contact, and V3 public classes remain. |
| Avery gives consent | D1 questionnaire and T1 normalized interests in Club Portal; V1 discovery interests and V2 yoga recommendation in Class Booking; P1 offer interests, C1 audience membership, and Q1 invitation in Member Offers. |
| Delete questionnaire only | D1 absent; **six linked records remain**; consent remains active. This is the deck’s “other apps still remember” moment. |
| Approved withdrawal completes | **Seven targets verified absent**, including D1 removed earlier. B1, D2, and V3 preserved. Consent withdrawn. |
| Replay old job | Re-import of V1 blocked; V1 remains absent. |

Avery’s interest is evening yoga **after 6 pm**. The recommendation is Wednesday yoga at 7 pm; the promotional taster is Thursday; the preserved paid booking is **Saturday strength at 10 am**. These are separate activities. Another synthetic member, Jordan, has matching yoga text; their records are outside Avery’s scope.

The shared persona illustration is story context, not a live stored-record indicator. It remains after withdrawal. Show the record cards, counts, and receipt as removal evidence. Member Offers’ decorative “Something selected for you” banner also remains; the personalized invitation must disappear.

At the alignment check, `.runtime/fitness` held the fresh opening state, while `.runtime/recording` held active consent with the questionnaire already removed. Saved folders do not identify which instance your browser uses. Follow the visible reset checks above; do not assume an existing tab is at the opening scene. No saved demo data was changed by this documentation update.

## Optional recovery take — swap for the detailed review and receipt tour

Use this variant when showing restart recovery matters more than inspecting model findings. It adds navigation and should be rehearsed within the same three-minute budget; otherwise record it as a separate follow-up.

1. Before approval, open Recall’s sidebar and select **Execution scenario → Worker restart after one deletion**; collapse the sidebar.
2. Approve normally. Show **Ready to resume** and the saved-progress warning. Say: “This is a simulated worker interruption after one deletion. Approval and completed work are saved.”
3. Reload Recall to demonstrate that the request survives a page reload. Click **Manage consent withdrawal ↓** to return to the receipt, then **Restore demo services & resume**.
4. Wait for **WITHDRAWAL VERIFIED**, the preservation checks, and outcome audit. Continue with the cross-app checks and replay.

Do not call this a real process crash. LangGraph coordinates model review and execution stages; the application’s SQLite engine persists approval and progress. This implementation does not use a LangGraph checkpointer or let model agents authorize deletions.

## Presenter guardrails

- Keep the core demo on Healthy services. Recovery, retry limits, clarification, and revoked approval are supported but not all exercised in this three-minute path. The optional take demonstrates interruption recovery.
- **Agent read-tool evidence** is farther down in **The evidence trail**. Use it for questions after the demo; traversing the full trace during the timed run crowds out the cross-app proof. The main run shows live tool progress and the returned review findings instead.
- Describe the findings actually returned. If clarification is requested, answer it; if review is blocked, do not claim a passed plan. If the model auditor is unavailable, resolve the provider issue and use **Verify again** before presenting a completed model audit.
- A partial result is not a verified withdrawal. Use **Restore demo services & resume** when appropriate and inspect the final result.
- Keep booking search empty and refresh customer screens explicitly. Reload Recall after changing consent or deleting the source in Club Portal.
- This demonstrates synthetic data in three connected local stores, not arbitrary external services, delivered messages, or model-training deletion. Model calls are real; deterministic service checks establish record presence. See [evaluation](EVALUATION.md) for measured evidence and its limits.
