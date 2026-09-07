from __future__ import annotations

from datetime import date
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

from subscription_logic import (
    analyze_subscriptions,
    category_spend,
    export_action_plan,
    load_subscriptions_csv,
    run_savings_scenario,
    summarize_spend,
)


APP_DIR = Path(__file__).parent
SAMPLE_CSV = APP_DIR / "sample_subscriptions.csv"


def currency(value: float) -> str:
    return f"${value:,.2f}"


def load_sample() -> pd.DataFrame:
    return load_subscriptions_csv(SAMPLE_CSV.read_text())


def display_metric(label: str, value: str, help_text: str | None = None) -> None:
    st.metric(label=label, value=value, help=help_text)


def bar_chart(data: pd.DataFrame, x: str, y: str, x_title: str, y_title: str, color: str) -> alt.Chart:
    return (
        alt.Chart(data)
        .mark_bar(color=color, cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X(
                f"{x}:N",
                title=x_title,
                sort="-y",
                axis=alt.Axis(labelAngle=0, labelLimit=180, labelPadding=10, titlePadding=18),
            ),
            y=alt.Y(
                f"{y}:Q",
                title=y_title,
                axis=alt.Axis(format="$,.0f", labelPadding=8, titlePadding=16),
            ),
            tooltip=[
                alt.Tooltip(f"{x}:N", title=x_title),
                alt.Tooltip(f"{y}:Q", title=y_title, format="$,.2f"),
            ],
        )
        .properties(
            background="#ffffff",
            height=340,
            padding={"left": 48, "right": 32, "top": 24, "bottom": 92},
        )
        .configure_view(fill="#ffffff", stroke="#d9e2dd")
        .configure_axis(
            domainColor="#9aaca3",
            gridColor="#e8eee9",
            labelColor="#17211c",
            labelFont="Arial",
            labelFontSize=13,
            titleColor="#17211c",
            titleFont="Arial",
            titleFontSize=14,
            titleFontWeight=700,
        )
    )


st.set_page_config(
    page_title="Subscription Reality Check",
    page_icon="",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --paper: #f8faf7;
        --ink: #17211c;
        --muted: #617069;
        --mint: #d8f3dc;
        --mint-strong: #1f8a5b;
        --coral: #ef6f61;
        --gold: #f4b942;
        --line: #d9e2dd;
    }
    .stApp {
        background: var(--paper);
        color: var(--ink);
    }
    h1, h2, h3 {
        font-family: "Trebuchet MS", Arial, sans-serif;
        color: var(--ink);
        letter-spacing: 0;
    }
    p, label, div {
        font-family: Arial, sans-serif;
    }
    p, label, span, small {
        color: var(--ink);
    }
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid var(--line);
        border-left: 5px solid var(--mint-strong);
        border-radius: 8px;
        padding: 14px 16px;
        box-shadow: 0 1px 0 rgba(23, 33, 28, 0.04);
    }
    [data-testid="stMetricValue"] {
        font-family: "Courier New", monospace;
        color: var(--ink);
    }
    section[data-testid="stSidebar"] {
        background: #edf4ef;
        border-right: 1px solid var(--line);
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] small {
        color: var(--ink);
    }
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] span {
        color: var(--muted);
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
        background: #ffffff;
        border: 1px dashed var(--mint-strong);
        border-radius: 8px;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button,
    div.stButton > button,
    div.stDownloadButton > button {
        background: #ffffff !important;
        background-color: #ffffff !important;
        border: 1px solid var(--line) !important;
        border-radius: 8px;
        color: var(--ink) !important;
        font-weight: 700;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button:hover,
    div.stButton > button:hover,
    div.stDownloadButton > button:hover {
        background: var(--mint) !important;
        background-color: var(--mint) !important;
        border-color: var(--mint-strong) !important;
        color: var(--ink) !important;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button:focus,
    div.stButton > button:focus,
    div.stDownloadButton > button:focus {
        border-color: var(--mint-strong) !important;
        box-shadow: 0 0 0 3px rgba(31, 138, 91, 0.18) !important;
        color: var(--ink) !important;
    }
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button *,
    section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button p,
    div.stButton > button *,
    div.stButton > button p,
    div.stDownloadButton > button *,
    div.stDownloadButton > button p {
        color: var(--ink) !important;
        font-weight: 700 !important;
    }
    button[data-baseweb="tab"] p {
        color: var(--ink);
        font-weight: 700;
    }
    button[data-baseweb="tab"]:hover p,
    button[data-baseweb="tab"]:focus p {
        color: var(--coral);
    }
    button[data-baseweb="tab"][aria-selected="true"] p {
        color: var(--coral);
    }
    div[data-baseweb="tab-highlight"] {
        background-color: var(--coral);
    }
    div[data-testid="stVegaLiteChart"],
    div[data-testid="stVegaLiteChart"] > div,
    .vega-embed,
    .vega-embed > div,
    .vega-embed canvas,
    .vega-embed svg {
        background: #ffffff !important;
        background-color: #ffffff !important;
    }
    .vega-embed svg text {
        fill: var(--ink) !important;
    }
    .vega-embed details,
    .vega-embed summary,
    .vega-embed .vega-actions {
        display: none !important;
    }
    button[aria-label="Show data"],
    button[aria-label="Fullscreen"],
    button[aria-label="View fullscreen"],
    button[title="Show data"],
    button[title="Fullscreen"],
    button[title="View fullscreen"],
    [data-testid="StyledToolbar"],
    [data-testid="stElementToolbar"],
    [data-testid="stElementToolbarButton"] {
        display: none !important;
        opacity: 0 !important;
        pointer-events: none !important;
        visibility: hidden !important;
    }
    div[data-testid="stAlert"] {
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "subscriptions" not in st.session_state:
    st.session_state.subscriptions = load_sample()

with st.sidebar:
    st.header("Data")
    st.caption("Use the sample file or upload your own CSV with the same columns.")
    uploaded = st.file_uploader("Upload subscriptions CSV", type=["csv"])

    if uploaded is not None:
        try:
            st.session_state.subscriptions = load_subscriptions_csv(uploaded.getvalue().decode("utf-8"))
            st.success("CSV loaded.")
        except ValueError as error:
            st.error(str(error))

    if st.button("Reload sample data", use_container_width=True):
        st.session_state.subscriptions = load_sample()
        st.rerun()

    st.download_button(
        "Download current data",
        data=st.session_state.subscriptions.to_csv(index=False),
        file_name="subscriptions.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.title("Subscription Reality Check")
st.caption("Track monthly costs and usage, then test what your spending looks like after canceling selected subscriptions.")

try:
    analyzed = analyze_subscriptions(st.session_state.subscriptions, today=date.today())
except ValueError as error:
    st.error(str(error))
    st.stop()

summary = summarize_spend(analyzed)
overview_tab, reality_tab, scenario_tab = st.tabs(["Overview", "Reality Check", "Savings Scenario"])

with overview_tab:
    metric_cols = st.columns(4)
    with metric_cols[0]:
        display_metric("Monthly spend", currency(summary["total_monthly"]))
    with metric_cols[1]:
        display_metric("Yearly spend", currency(summary["total_yearly"]))
    with metric_cols[2]:
        display_metric("Subscriptions", str(summary["subscription_count"]))
    with metric_cols[3]:
        display_metric("High-risk items", str(summary["high_risk_count"]))

    st.subheader("Spending by category")
    category_totals = category_spend(analyzed)
    st.altair_chart(
        bar_chart(
            category_totals,
            x="category",
            y="monthly_cost",
            x_title="Category",
            y_title="Monthly cost",
            color="#1f8a5b",
        ),
        use_container_width=True,
        theme=None,
    )

    st.dataframe(
        category_totals.rename(
            columns={
                "category": "Category",
                "monthly_cost": "Monthly cost",
                "yearly_cost": "Yearly cost",
            }
        ),
        hide_index=True,
        use_container_width=True,
    )

with reality_tab:
    st.subheader("Cost per use")
    st.caption("High score means the subscription is expensive, low-use, close to renewal, or low importance.")

    table = analyzed[
        [
            "name",
            "category",
            "monthly_cost",
            "uses_per_month",
            "cost_per_use",
            "yearly_cost",
            "renewal_date",
            "days_until_renewal",
            "importance",
            "reality_score",
            "risk_level",
            "recommendation",
        ]
    ].rename(
        columns={
            "name": "Name",
            "category": "Category",
            "monthly_cost": "Monthly cost",
            "uses_per_month": "Uses/month",
            "cost_per_use": "Cost/use",
            "yearly_cost": "Yearly cost",
            "renewal_date": "Renewal date",
            "days_until_renewal": "Days until renewal",
            "importance": "Importance",
            "reality_score": "Reality score",
            "risk_level": "Risk",
            "recommendation": "Recommendation",
        }
    )

    st.dataframe(
        table,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Monthly cost": st.column_config.NumberColumn(format="$%.2f"),
            "Cost/use": st.column_config.NumberColumn(format="$%.2f"),
            "Yearly cost": st.column_config.NumberColumn(format="$%.2f"),
            "Reality score": st.column_config.ProgressColumn(min_value=0, max_value=100),
        },
    )

    upcoming = analyzed[analyzed["days_until_renewal"].between(0, 14)]
    if upcoming.empty:
        st.success("No renewals in the next 14 days.")
    else:
        st.warning("Renewals coming up in the next 14 days.")
        st.dataframe(
            upcoming[["name", "monthly_cost", "renewal_date", "days_until_renewal", "recommendation"]].rename(
                columns={
                    "name": "Name",
                    "monthly_cost": "Monthly cost",
                    "renewal_date": "Renewal date",
                    "days_until_renewal": "Days until renewal",
                    "recommendation": "Recommendation",
                }
            ),
            hide_index=True,
            use_container_width=True,
        )

with scenario_tab:
    st.subheader("What happens if I remove these?")

    default_removals = analyzed.head(2)["name"].tolist()
    selected_removals = st.multiselect(
        "Subscriptions to exclude from spending",
        options=analyzed["name"].tolist(),
        default=default_removals,
    )

    scenario = run_savings_scenario(analyzed, selected_removals)
    scenario_cols = st.columns(4)
    with scenario_cols[0]:
        display_metric("Current yearly", currency(scenario.current_yearly))
    with scenario_cols[1]:
        display_metric("New yearly", currency(scenario.new_yearly))
    with scenario_cols[2]:
        display_metric("Yearly savings", currency(scenario.yearly_savings))
    with scenario_cols[3]:
        display_metric("Monthly savings", currency(scenario.monthly_savings))

    comparison = pd.DataFrame(
        [
            {"Plan": "Current", "Monthly spend": scenario.current_monthly, "Yearly spend": scenario.current_yearly},
            {"Plan": "After removals", "Monthly spend": scenario.new_monthly, "Yearly spend": scenario.new_yearly},
        ]
    )
    st.altair_chart(
        bar_chart(
            comparison,
            x="Plan",
            y="Yearly spend",
            x_title="Plan",
            y_title="Yearly spend",
            color="#ef6f61",
        ),
        use_container_width=True,
        theme=None,
    )

    selected_plan = analyzed[analyzed["name"].isin(selected_removals)]
    if selected_plan.empty:
        st.info("Select one or more subscriptions to see a cancellation plan.")
    else:
        st.dataframe(
            selected_plan[["name", "category", "monthly_cost", "uses_per_month", "cost_per_use", "yearly_cost"]].rename(
                columns={
                    "name": "Name",
                    "category": "Category",
                    "monthly_cost": "Monthly cost",
                    "uses_per_month": "Uses/month",
                    "cost_per_use": "Cost/use",
                    "yearly_cost": "Yearly cost",
                }
            ),
            hide_index=True,
            use_container_width=True,
            column_config={
                "Monthly cost": st.column_config.NumberColumn(format="$%.2f"),
                "Cost/use": st.column_config.NumberColumn(format="$%.2f"),
                "Yearly cost": st.column_config.NumberColumn(format="$%.2f"),
            },
        )

    st.download_button(
        "Download cancellation action plan",
        data=export_action_plan(analyzed, selected_removals),
        file_name="cancellation_action_plan.csv",
        mime="text/csv",
        use_container_width=True,
    )
