# Week 1 Project: Subscription Reality Check

## Project Overview

Subscription Reality Check is a Streamlit data app that helps users understand recurring subscription spending. It tracks monthly costs and monthly usage, calculates cost per use, shows spending by category, and lets the user select subscriptions to exclude in a savings scenario.

The main question answered by the app is:

> What happens to my yearly spending if I remove these subscriptions?

## Problem Statement

I often sign up for subscriptions when I am interested in a new product, tool, or trial. Over time, I may forget to cancel subscriptions that I no longer use often. This creates hidden recurring spending. The app turns a simple subscription list into practical insights so I can decide what to keep, review, or cancel.

## Dataset

The project uses a synthetic CSV dataset with realistic subscription examples. The dataset does not contain personal financial data.

Columns:

```text
name
category
monthly_cost
uses_per_month
renewal_date
importance
notes
```

Example subscriptions include AI tools, design tools, streaming services, learning platforms, food trials, and health apps.

## App Workflow

1. Load the sample subscription CSV or upload a custom CSV.
2. View total monthly and yearly subscription spending.
3. Review spending by category.
4. Review cost per use and the reality score for each subscription.
5. Select subscriptions to remove from the savings scenario.
6. Compare current yearly spending with the new yearly spending.
7. Export a cancellation action plan.

## Technical Implementation

The project uses Python, Streamlit, Pandas, and Pytest.

The calculation logic is separated into `subscription_logic.py` so it can be tested independently from the UI. The app validates required CSV columns, cleans numeric and date fields, calculates yearly cost, calculates cost per use, scores subscriptions, groups spending by category, and runs savings simulations.

## Local Setup

The app can be run locally inside a Python virtual environment:

```bash
cd /Users/maneettaantony/Workspaces/genai-academy-projects
python3 -m venv week1/subscription-reality-check/.venv
source week1/subscription-reality-check/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r week1/subscription-reality-check/requirements.txt
streamlit run week1/subscription-reality-check/app.py
```

Tests can be run with:

```bash
python -m pytest week1/subscription-reality-check
```

## Cloud Deployment Plan

The preferred deployment option is Streamlit Community Cloud because this project is built with Streamlit.

Deployment settings:

```text
Repository: GitHub repository for this project
Branch: main
Main file path: week1/subscription-reality-check/app.py
Python version: 3.12
```

The app is designed to run from the repository root locally and on Streamlit Community Cloud. The `requirements.txt` file is kept in the same folder as `app.py`, and the repository-level `.streamlit/config.toml` keeps the theme consistent across environments.

After deployment, the Streamlit app URL can be added here:

```text
Live app URL: <add Streamlit Community Cloud URL>
GitHub repo URL: <add GitHub repo URL>
```

## AI-Assisted Coding Prompts

Prompt 1:

> I need to build a week 1 project meeting the expectations provided in the handout. Help me with a few creative and real-world use cases, most relevant day-to-day life examples which I can build in an hour or so.

Prompt 2:

> I am looking for code-heavy track where can I write/code.

Prompt 3:

> I did not like the expense splitter. Can we change the idea to Subscription Reality Check in an advanced code-heavy path to meet the Week 1 expectations? It closely relates to me missing my subscription cancellations as I keep adding subscriptions mostly when I am interested in a new product and forget.

Prompt 4:

> Let's brainstorm and build the plan first. Make sure to keep it simple with suggested workflow but complex enough to code.

Prompt 5:

> I hope we are talking about this: Subscription Reality Check. Losing track of recurring subscriptions and how often you use them. Track monthly costs and uses; calculate cost per use; show spending by category; select subscriptions to exclude in a savings scenario. What happens to my yearly spending if I remove these two?

## Iterations

Initial idea considered: shared expense splitter.

Reason for pivot: The subscription idea was more personally relevant and better matched a day-to-day problem I experience.

Final direction: A CSV-based subscription analysis app focused on usage, cost per use, category spending, and savings scenarios.

## Screenshots To Add

- Screenshot 1: App overview dashboard.
- Screenshot 2: Reality Check table with cost per use and score.
- Screenshot 3: Savings Scenario tab after selecting subscriptions to remove.
- Screenshot 4: Code showing calculation logic.
- Screenshot 5: Test results.

## Learnings

- I learned how to turn a personal problem into a data application.
- I practiced separating UI code from calculation logic.
- I learned how to validate CSV data before analysis.
- I used tests to verify calculations such as yearly spending and savings scenarios.
- I practiced using AI as a coding collaborator while still reviewing and shaping the project direction.

## Limitations

- The first version assumes every subscription has a monthly cost.
- The app does not connect to bank accounts or payment providers.
- The data is synthetic unless the user uploads their own CSV.
- The cancellation action plan is exported as CSV, but the app does not cancel subscriptions automatically.

## Future Enhancements

- Support weekly, quarterly, and yearly billing cycles.
- Add reminders for renewals within 7 days.
- Add a database so subscriptions persist after closing the browser.
- Add charts for spending trends over time.
- Add a budget goal and show how many subscriptions must be removed to reach it.
