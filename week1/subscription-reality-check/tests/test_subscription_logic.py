from datetime import date

import pandas as pd
import pytest

from subscription_logic import (
    analyze_subscriptions,
    calculate_cost_per_use,
    category_spend,
    export_action_plan,
    load_subscriptions_csv,
    run_savings_scenario,
    summarize_spend,
)


def example_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "name": "Tool A",
                "category": "AI Tools",
                "monthly_cost": 20.00,
                "uses_per_month": 10,
                "renewal_date": "2026-09-20",
                "importance": "High",
                "notes": "Used often",
            },
            {
                "name": "Forgotten Trial",
                "category": "Food",
                "monthly_cost": 45.00,
                "uses_per_month": 0,
                "renewal_date": "2026-09-10",
                "importance": "Low",
                "notes": "Cancel soon",
            },
            {
                "name": "Design App",
                "category": "Design",
                "monthly_cost": 14.99,
                "uses_per_month": 1,
                "renewal_date": "2026-09-11",
                "importance": "Low",
                "notes": "One-time project",
            },
        ]
    )


def test_cost_per_use_handles_zero_usage() -> None:
    assert calculate_cost_per_use(12.99, 0) == 12.99
    assert calculate_cost_per_use(20.00, 8) == 2.5


def test_analyze_subscriptions_adds_ranked_reality_fields() -> None:
    analyzed = analyze_subscriptions(example_df(), today=date(2026, 9, 7))

    assert analyzed.iloc[0]["name"] == "Forgotten Trial"
    assert analyzed.iloc[0]["risk_level"] == "High"
    assert analyzed.iloc[0]["days_until_renewal"] == 3
    assert analyzed.iloc[0]["yearly_cost"] == 540.00


def test_summarize_spend_calculates_totals() -> None:
    analyzed = analyze_subscriptions(example_df(), today=date(2026, 9, 7))
    summary = summarize_spend(analyzed)

    assert summary["subscription_count"] == 3
    assert summary["total_monthly"] == 79.99
    assert summary["total_yearly"] == 959.88
    assert summary["high_risk_count"] == 2


def test_category_spend_groups_monthly_and_yearly_costs() -> None:
    analyzed = analyze_subscriptions(example_df(), today=date(2026, 9, 7))
    grouped = category_spend(analyzed)

    assert grouped.iloc[0]["category"] == "Food"
    assert grouped.iloc[0]["monthly_cost"] == 45.00
    assert grouped.iloc[0]["yearly_cost"] == 540.00


def test_run_savings_scenario_answers_remove_these_question() -> None:
    analyzed = analyze_subscriptions(example_df(), today=date(2026, 9, 7))
    scenario = run_savings_scenario(analyzed, ["Forgotten Trial", "Design App"])

    assert scenario.current_monthly == 79.99
    assert scenario.new_monthly == 20.00
    assert scenario.yearly_savings == 719.88


def test_load_csv_requires_expected_columns() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        load_subscriptions_csv("name,monthly_cost\nNetflix,15.49")


def test_export_action_plan_contains_selected_subscriptions() -> None:
    analyzed = analyze_subscriptions(example_df(), today=date(2026, 9, 7))
    exported = export_action_plan(analyzed, ["Design App"])

    assert "Design App" in exported
    assert "Forgotten Trial" not in exported
