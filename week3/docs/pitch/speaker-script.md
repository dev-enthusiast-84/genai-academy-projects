# Recall — two-minute recording script

294 spoken words. Budget 110 seconds for narration and 10 seconds for slide changes. Use the quoted narration as a conversational guide, not text to recite mechanically. Pause at the story beats; the delivery cues are not spoken.

## Slide 1 · 0:00–0:24 · Meet Avery. One fitness club. Three apps.

**Delivery cue:** Introduce Avery as a person first. Explain what each app does before discussing withdrawal.

> Meet Avery, a member of a fitness club in our demo. Avery fills in a questionnaire in Club Portal and agrees to share an interest in evening yoga. Class Booking uses it to recommend classes. Member Offers prepares a yoga invitation. Avery also has a paid Saturday booking. Everything is useful—until Avery decides they no longer want that personalization.

## Slide 2 · 0:24–0:48 · Avery changes their mind. The other apps still remember.

**Delivery cue:** Pause after “the copies remain.” Introduce Recall explicitly as the fourth app: the privacy dashboard.

> Avery deletes the questionnaire, but the recommendation and invitation remain. The source is gone; the copies remain. Recall is our separate privacy dashboard for fixing that gap. Avery asks: stop using my yoga interests, but keep my paid class. Recall traces the linked records, presents a removal plan, waits for approval, and verifies the result across all three apps.

## Slide 3 · 0:48–1:11 · Stop personalization. Keep the membership working.

**Delivery cue:** Emphasize the contrast between stopping personalization and keeping the paid class. These are the promises the final slide will verify.

> Avery is not asking to leave the club. They want three things: remove the shared interests and the recommendations built from them; keep the paid class and membership; and stop old copies coming back. Deleting everything would be easy to explain—and wrong. Recall has to make a precise change, then show that the rest still works.

## Slide 4 · 1:11–1:35 · Three agents. A separate judge. LangGraph coordinates the work.

**Delivery cue:** Introduce each model role along the diagram. Pause at Avery’s approval, then follow the return path through verification and the outcome auditor.

> That precision takes a team with distinct roles. The investigator agent traces copies. The scope reviewer checks what belongs in the plan. A separate judge model challenges it. LangGraph coordinates those handoffs and bounded repairs. Avery alone approves the writes. After execution, service checks feed the outcome auditor agent. SQLite saves approval and progress, so interrupted work can resume.

## Slide 5 · 1:35–2:00 · Copies removed. Paid booking preserved.

**Delivery cue:** Connect the result back to Avery’s original request. Pause on the preserved booking, then close with the benefit.

> Now Avery’s request has a visible result. The recommendation and invitation disappear. Seven targets are verified absent, including the questionnaire deleted earlier. The paid Saturday class remains confirmed. An old import tries to restore a withdrawn preference; it is blocked. Avery can change their privacy choice without losing the service they paid for. That is Recall: consent with an undo button.

## Presenter checks — do not read aloud

- Start with a fresh demo for the opening scene; follow the [three-minute walkthrough](../demo-script-3-min.md).
- Reload Recall after changes in Club Portal. Refresh Class Booking and Member Offers explicitly and keep the booking search empty.
- The invitation is a local preview, not a delivered message. Seven verified-absent targets includes the source already deleted and six linked records.
- Confirm configured models match Slide 4 before recording. Use a fresh receipt and actual model findings; see [evaluation](../EVALUATION.md) for the isolated live-run evidence.
- The 9/10 timing claim remains a target; a single smoke test or edited video does not establish reliability.


## Recording and rebuilding

This two-minute pitch is separate from the [three-minute application demo](../demo-script-3-min.md).

Open the [HTML deck](recall-pitch.html) or [PDF](recall-pitch-deck.pdf). HTML controls: arrow keys advance, **N** shows the script, **Escape** shows all slides. Read only the quoted paragraphs above.

Rebuild from `week3/` with `.venv/bin/python docs/pitch/build_deck.py --pdf`. HTML/script generation uses Python’s standard library. PDF export needs `requirements-browser.txt` and Playwright Chromium. Omit `--pdf` when only HTML and the speaker script are needed. The generator holds slide content/narration and preserves these presenter notes.
