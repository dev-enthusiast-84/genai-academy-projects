# Almost Qualified — two-minute slide walkthrough

Approximately 275 spoken words. Aim for about 140 words per minute, with brief pauses when changing slides.

## Slide 1 — The problem · 0:00–0:22

Career changers often have useful experience, but struggle to connect it to a job description. A matching keyword doesn’t prove they meet a requirement. For example, writing deployment instructions isn’t the same as running an application in production. Almost Qualified helps answer a more useful question: what can I actually back up?

## Slide 2 — The solution and one-liner · 0:22–0:49

Following the project handout’s one-liner: my RAG app helps career changers identify supported job requirements and missing evidence, from one resume, two project artifacts, and three saved job descriptions, in a Streamlit workspace. The targets are 95 percent faithfulness and 80 percent retrieval precision at five. These are goals, not results claimed here. The demo uses fictional documents.

## Slide 3 — Features and walkthrough · 0:49–1:13

Choose a saved role and up to five requirements. The app labels each as supported, partially supported, or no evidence found, with explanations and citation excerpts. In this example, deployment is only partially supported. The next step is to document an actual deployment and your contribution. You can download the assessment for interview preparation.

## Slide 4 — Architecture · 1:13–1:37

Only EvidenceAgent uses an LLM: GPT-4 Turbo by default, through LiteLLM. The alternatives shown are GPT-4o mini, Gemini 2.0 Flash, and Claude 3.5 Sonnet; you select one. Parsing, BM25 retrieval, and citation validation use Python, not LLMs. Without a key, assessment uses local rules. Job descriptions provide requirements; candidate documents provide proof.

## Slide 5 — Why this approach · 1:37–2:00

RAG makes the reasoning inspectable. Local BM25 keeps this small demo simple, and Streamlit makes it easy to try. Local mode works without an API key. Keyword search can miss paraphrases, so evaluation comes before adding more complexity. The value is practical: know what you can support today, and what evidence to add next.
