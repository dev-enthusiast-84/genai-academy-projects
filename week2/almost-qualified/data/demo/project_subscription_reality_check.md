# Project write-up: Subscription Reality Check

Document category: candidate

## Problem

People often keep recurring subscriptions after usage drops. The project asks what yearly spending changes when selected subscriptions are removed.

## What was built

The app loads sample subscription data or a user-uploaded CSV, validates required columns, calculates monthly and yearly spend, computes cost per use, ranks subscriptions with a reality score, and exports a cancellation action plan.

## Technical details

- Framework: Streamlit
- Data tools: pandas and Altair
- Tests: pytest unit tests for validation and scoring behavior
- Deployment plan: Streamlit Community Cloud instructions documented in the README
- Runtime: Python 3.12

## Evidence boundaries

The README describes how to deploy the app. It does not prove that the app was deployed, monitored, or used by real external users.
