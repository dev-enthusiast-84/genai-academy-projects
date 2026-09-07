# Video Script

Target length: 4 to 5 minutes.

## 0:00 - 0:30 Problem

Hi, this is my Week 1 project: Subscription Reality Check.

I built this because I often sign up for subscriptions when I am interested in a new tool, product, or trial, but later I forget to cancel some of them. The goal of the app is to make recurring spending visible and answer one practical question: what happens to my yearly spending if I remove selected subscriptions?

## 0:30 - 1:10 Dataset

The app uses a CSV dataset with subscription name, category, monthly cost, monthly usage, renewal date, importance, and notes.

For the demo I am using synthetic data, including tools like ChatGPT Plus, Canva Pro, Netflix, Spotify, a meal kit trial, learning platforms, and health apps.

## 1:10 - 2:00 Overview

On the Overview tab, the app calculates total monthly spending, total yearly spending, subscription count, and high-risk items.

It also groups spending by category so I can see where most of my recurring money goes.

## 2:00 - 3:00 Reality Check

On the Reality Check tab, the app calculates cost per use for each subscription.

For example, a subscription that costs a lot but is used once per month becomes expensive per use. The app also creates a reality score based on monthly cost, usage, renewal timing, and importance. This helps identify subscriptions that should be reviewed first.

## 3:00 - 4:00 Savings Scenario

On the Savings Scenario tab, I can select subscriptions to remove.

The app recalculates current yearly spending, new yearly spending, monthly savings, and yearly savings. This directly answers the project question: what happens to my yearly spending if I remove these two subscriptions?

I can also export a cancellation action plan as a CSV.

## 4:00 - 5:00 AI-Assisted Workflow

I used AI to brainstorm project ideas, compare possible use cases, and then refine the project into a code-heavy but manageable Streamlit app.

The main iteration was switching from a shared expense splitter to Subscription Reality Check because the subscription problem was more personally relevant.

I also used AI to help structure the calculation logic, create tests, draft the submission artifacts, and prepare deployment instructions. My main learning was how to separate the app into a UI layer and a calculation layer so the business logic can be tested independently.

For deployment, I prepared the app for Streamlit Community Cloud. The main file path is `week1/subscription-reality-check/app.py`, and the dependencies are listed in `requirements.txt`.
