# Hosted fitness demo

See [Deployment](deployment.md) for synchronizing public artifacts and configuring GitHub Pages.

## Pages

- `scenario.html`: optional overview showing all three customer apps together.
- `club-portal.html`: membership and explicit consent.
- `class-booking.html`: paid booking and personalized recommendations.
- `member-offers.html`: personalized invitation preview.
- `index.html`: Recall, the separate agent app.

## Five-minute flow

1. Open the scenario overview. Show three distinct apps without personalization.
2. Agree to sharing in Club Portal. Watch the class recommendation and invitation appear automatically under the same consent.
3. Delete only the questionnaire. The other apps still personalize: this is the problem.
4. Open Recall. Connect a model, investigate, review the evidenced plan, and approve withdrawal. The labeled sample route is available for workflow rehearsal only.
5. Show the recommendation and invitation disappear while the paid booking remains. Replay old sharing and verify it is blocked.

Optional failure: choose Member Offers offline before approval, show the partial result, reload, then restore and resume.

## Scope

All four pages are functional browser apps using separate simulated service records in browser storage. They are not independently hosted backend services. The Python connected-app version provides separate local processes and databases. Keys remain in memory; no key is published. Model-based investigation needs your provider connection.
