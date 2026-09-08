# Subscription Reality Check

Subscription Reality Check is a Streamlit data app for tracking recurring subscriptions, measuring cost per use, and simulating yearly savings when selected subscriptions are removed.

## Problem

It is easy to sign up for tools, trials, and services when they feel useful in the moment, then forget about them when usage drops. This app helps answer a practical question:

> What happens to my yearly spending if I remove these subscriptions?

## Features

- Load a sample subscription dataset or upload a CSV.
- Calculate monthly spend, yearly spend, and cost per use.
- Show spending by category.
- Rank subscriptions with a reality score based on cost, usage, renewal timing, and importance.
- Select subscriptions to exclude in a savings scenario.
- Export a cancellation action plan as CSV.

## Dataset Format

The app expects a CSV with these columns:

```text
name,category,monthly_cost,uses_per_month,renewal_date,importance,notes
```

`renewal_date` must use `YYYY-MM-DD`. `importance` must be `Low`, `Medium`, or `High`.

## Run Locally

Run the app from the repository root. This matches how Streamlit Community Cloud runs apps with entrypoint files in subdirectories.

```bash
cd /Users/maneettaantony/Workspaces/genai-academy-projects
python3 -m venv week1/subscription-reality-check/.venv
source week1/subscription-reality-check/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r week1/subscription-reality-check/requirements.txt
streamlit run week1/subscription-reality-check/app.py
```

The app opens at `http://localhost:8501`.

## Run Tests

```bash
cd /Users/maneettaantony/Workspaces/genai-academy-projects
source week1/subscription-reality-check/.venv/bin/activate
python -m pytest
```

If packages are already installed globally, you can run:

```bash
python3 -m pytest week1/subscription-reality-check
python3 -m streamlit run week1/subscription-reality-check/app.py
```

## Deploy To Streamlit Community Cloud

1. Push this repository to GitHub.
2. Go to `https://share.streamlit.io`.
3. Sign in with GitHub.
4. Click `Create app`.
5. Select the repository and branch.
6. Use this main file path:

```text
week1/subscription-reality-check/app.py
```

7. In advanced settings, select Python `3.12` if available.
8. Deploy the app.

Streamlit Community Cloud runs the app from the repository root. Because the entrypoint file is in a subdirectory, this project keeps `requirements.txt` next to `app.py`, which Streamlit Community Cloud supports. The repository-level `.streamlit/config.toml` sets the light theme for both local and cloud runs.

This project includes `runtime.txt` with `python-3.12` to document the intended remote Python version. If Streamlit Cloud offers a Python version selector, choose Python `3.12`.

## Deployment Files

```text
app.py
requirements.txt
runtime.txt
sample_subscriptions.csv
subscription_logic.py
.streamlit/config.toml
```

## Code Structure

- `app.py`: Streamlit interface and user workflow.
- `subscription_logic.py`: CSV validation, calculations, scoring, savings scenario, and export logic.
- `sample_subscriptions.csv`: Synthetic data used for the demo.
- `tests/test_subscription_logic.py`: Unit tests for the main calculation behavior.
- `runtime.txt`: Intended Python version for cloud deployment.
- `showcase.html`: Project-owned case study page referenced from the root GitHub Pages site.

## Hands-On Coding Practice

Good places to practice coding:

1. Change the scoring formula in `score_subscription`.
2. Add a new `billing_cycle` column and convert weekly or yearly plans to monthly cost.
3. Add a filter for categories.
4. Add a chart for cost per use.
5. Add a new savings scenario such as "remove all low-importance subscriptions."
6. Add tests before and after each logic change.
