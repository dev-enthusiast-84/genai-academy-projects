from __future__ import annotations

import json

import streamlit as st

from agent import EvidenceAgent, render_markdown
from model_config import MODEL_CATALOG, check_model_ready, get_api_key, resolve_model
from rag import build_manifest, extract_requirements, load_chunks, load_jobs


st.set_page_config(page_title="Almost Qualified", page_icon="AQ", layout="wide")

st.markdown(
    """
    <style>
    :root {
      --aq-ink: #1f2933;
      --aq-muted: #5d6875;
      --aq-panel: #f7f3ef;
      --aq-rule: #d7c9bc;
      --aq-blue: #316b83;
      --aq-green: #3f7f5f;
      --aq-gold: #a66f1f;
      --aq-red: #9b4242;
    }
    .stApp {
      background: linear-gradient(90deg, #fbfaf8 0 28%, #f4eee8 28% 29%, #fbfaf8 29% 100%);
      color: var(--aq-ink);
    }
    .block-container {
      padding-top: 2.5rem;
      max-width: 1180px;
    }
    h1 {
      color: var(--aq-ink);
      font-size: 2.6rem;
      line-height: 1;
      letter-spacing: 0;
      border-bottom: 2px solid var(--aq-rule);
      padding-bottom: 0.55rem;
    }
    h2, h3 {
      letter-spacing: 0;
      color: var(--aq-ink);
    }
    [data-testid="stMetricValue"] {
      color: var(--aq-blue);
    }
    div[data-testid="stDataFrame"] {
      border: 1px solid var(--aq-rule);
      border-radius: 6px;
      overflow: hidden;
    }
    .aq-callout {
      border-left: 5px solid var(--aq-blue);
      background: rgba(247, 243, 239, 0.9);
      padding: 0.8rem 1rem;
      margin: 0.5rem 0 1.25rem;
    }
    .aq-small {
      color: var(--aq-muted);
      font-size: 0.92rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def ensure_manifest() -> None:
    if "manifest_ready" not in st.session_state:
        build_manifest()
        st.session_state.manifest_ready = True


def configure_model() -> tuple[object | None, str, bool]:
    labels = [item.display_name for item in MODEL_CATALOG]
    default_label = labels[0]
    with st.sidebar:
        st.header("Model")
        selected = st.selectbox("Provider and model", labels, index=labels.index(default_label))
        advanced = st.toggle("Edit model ID")
        custom_model = ""
        if advanced:
            custom_model = st.text_input("Model ID", value=resolve_model(selected).model_id)
        option = resolve_model(selected, custom_model.strip() or None)
        use_model = st.toggle("Use model assessment", value=bool(option), help="Turn off to test retrieval without API calls.")
        temporary_key = st.text_input("Temporary API key", type="password", help="Kept only for this browser session.")
        api_key, key_source = get_api_key(option, temporary_key)
        st.caption(f"Key source: {key_source}")
        if st.button("Check model"):
            ok, message = check_model_ready(option, api_key)
            st.session_state.model_check = (ok, message)
        if "model_check" in st.session_state:
            ok, message = st.session_state.model_check
            (st.success if ok else st.warning)(message)
    return option, api_key, use_model


def status_color(status: str) -> str:
    return {
        "Supported": "#3f7f5f",
        "Partially supported": "#a66f1f",
        "No evidence found": "#9b4242",
    }.get(status, "#5d6875")


ensure_manifest()
model_option, api_key, use_model = configure_model()
chunks = load_chunks()
jobs = load_jobs()

st.title("Almost Qualified")
st.markdown(
    '<div class="aq-callout">Map job requirements to candidate evidence. The app cites what the corpus proves, flags gaps, and keeps the job description out of the evidence pool.</div>',
    unsafe_allow_html=True,
)

left, right = st.columns([0.36, 0.64], gap="large")

with left:
    st.subheader("Role")
    selected_job = st.selectbox("Saved job description", sorted(jobs))
    requirements = extract_requirements(jobs[selected_job])
    selected_ids = st.multiselect(
        "Requirements to assess",
        [item["requirement_id"] for item in requirements],
        default=[item["requirement_id"] for item in requirements[:5]],
        max_selections=5,
        format_func=lambda req_id: f"{req_id} - {next(item['text'] for item in requirements if item['requirement_id'] == req_id)}",
    )
    selected_requirements = [item for item in requirements if item["requirement_id"] in selected_ids]

    st.subheader("Corpus")
    candidate_chunks = [chunk for chunk in chunks if chunk.category == "candidate"]
    job_chunks = [chunk for chunk in chunks if chunk.category == "job"]
    cols = st.columns(3)
    cols[0].metric("Candidate chunks", len(candidate_chunks))
    cols[1].metric("Job chunks", len(job_chunks))
    cols[2].metric("Max rows", 5)

    run = st.button("Assess evidence", type="primary", width="stretch", disabled=not selected_requirements)

with right:
    st.subheader("Requirement preview")
    st.dataframe(
        [
            {
                "id": item["requirement_id"],
                "requirement": item["text"],
                "source": item["citation"],
            }
            for item in requirements
        ],
        hide_index=True,
        width="stretch",
    )

if run:
    with st.spinner("Retrieving candidate evidence and checking support..."):
        agent = EvidenceAgent(chunks, model_option=model_option, api_key=api_key)
        rows, errors = agent.assess(selected_requirements, use_model=use_model and bool(api_key))
        st.session_state.rows = rows
        st.session_state.errors = errors

if "errors" in st.session_state and st.session_state.errors:
    st.warning("Validation notes: " + "; ".join(st.session_state.errors))

if "rows" in st.session_state:
    rows = st.session_state.rows
    st.subheader("Assessment")
    for row in rows:
        border = status_color(row.status)
        st.markdown(
            f"""
            <div style="border-left: 6px solid {border}; padding: 0.5rem 0 0.5rem 1rem; margin-top: 0.75rem;">
              <strong>{row.requirement_id}: {row.status}</strong><br>
              <span class="aq-small">{row.requirement_text}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write(row.explanation)
        if row.conflict_flag:
            st.info("Conflict flag: at least one citation limits or narrows the claim.")
        if row.evidence:
            with st.expander("Evidence excerpts", expanded=True):
                for item in row.evidence:
                    st.markdown(f"**{item.source_title}** `{item.chunk_id}`")
                    st.caption(item.excerpt)
        if row.missing_evidence:
            st.caption(f"Missing evidence: {row.missing_evidence}")
        st.caption(f"Next step: {row.suggested_next_step}")

    report = render_markdown(rows)
    st.download_button("Download assessment", report, file_name="almost-qualified-assessment.md", mime="text/markdown")

    with st.expander("Raw structured output"):
        st.code(json.dumps([row.to_dict() for row in rows], indent=2), language="json")
