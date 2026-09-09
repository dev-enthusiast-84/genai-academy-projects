# Almost Qualified: Week 2 RAG App

## Overview

Almost Qualified helps career changers answer which job requirements their documented experience supports and what evidence is missing. The app uses a bounded corpus of candidate documents and job descriptions, retrieves candidate evidence, and returns requirement-level assessments with citations.

## RAG Framework

The app chunks candidate and job documents separately. During assessment, the retrieval tool searches only candidate chunks, so job descriptions cannot become proof of candidate experience. A single agent receives selected requirements and retrieved evidence, then returns structured rows. A validator checks status values, citation IDs, and exact excerpt membership.

## Corpus

The demo corpus is fictional and safe to share. It contains one resume-like document, two project artifacts, and three saved job descriptions.

## Surface

The app runs in Streamlit. Users choose a role, select up to five requirements, inspect results, open evidence excerpts, and download a Markdown report.

## Model Choice

The app supports a model selector through LiteLLM. OpenRouter is the recommended first route because one API key can reach many models. The app also runs in deterministic local mode for UI and retrieval testing.

## Evaluation

The demo includes labeled cases for direct support, partial support, unsupported requirements, and source-boundary behavior. The target is 95% faithfulness and 80% retrieval precision@5; actual measured results should be reported after running `evaluate.py`.
