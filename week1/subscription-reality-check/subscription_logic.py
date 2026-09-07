from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from io import StringIO

import pandas as pd


REQUIRED_COLUMNS = {
    "name",
    "category",
    "monthly_cost",
    "uses_per_month",
    "renewal_date",
    "importance",
    "notes",
}

EXPORT_COLUMNS = [
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
    "notes",
]


@dataclass(frozen=True)
class ScenarioResult:
    removed_names: tuple[str, ...]
    current_monthly: float
    new_monthly: float
    monthly_savings: float
    current_yearly: float
    new_yearly: float
    yearly_savings: float


def money(value: float | int | Decimal) -> float:
    """Round money values the same way humans expect currency to round."""
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def validate_columns(df: pd.DataFrame) -> None:
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")


def parse_money(value: object, field_name: str) -> float:
    try:
        amount = Decimal(str(value).strip())
    except (InvalidOperation, AttributeError):
        raise ValueError(f"{field_name} must be a valid number") from None

    if not amount.is_finite() or amount < 0:
        raise ValueError(f"{field_name} must be a positive number or zero")

    return money(amount)


def parse_non_negative_int(value: object, field_name: str) -> int:
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a whole number") from None

    if parsed < 0:
        raise ValueError(f"{field_name} cannot be negative")

    return parsed


def parse_date(value: object, field_name: str) -> date:
    text = str(value).strip()
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format") from None


def load_subscriptions_csv(csv_text: str) -> pd.DataFrame:
    df = pd.read_csv(StringIO(csv_text.strip()))
    validate_columns(df)
    return clean_subscriptions(df)


def clean_subscriptions(df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(df)
    records = []

    for row_number, row in df.iterrows():
        name = str(row["name"]).strip()
        category = str(row["category"]).strip()
        importance = str(row["importance"]).strip().title()
        notes = "" if pd.isna(row["notes"]) else str(row["notes"]).strip()

        if not name:
            raise ValueError(f"Row {row_number + 2}: name is required")
        if not category:
            raise ValueError(f"Row {row_number + 2}: category is required")
        if importance not in {"Low", "Medium", "High"}:
            raise ValueError(f"Row {row_number + 2}: importance must be Low, Medium, or High")

        monthly_cost = parse_money(row["monthly_cost"], f"Row {row_number + 2}: monthly_cost")
        uses_per_month = parse_non_negative_int(row["uses_per_month"], f"Row {row_number + 2}: uses_per_month")
        renewal_date = parse_date(row["renewal_date"], f"Row {row_number + 2}: renewal_date")

        records.append(
            {
                "name": name,
                "category": category,
                "monthly_cost": monthly_cost,
                "uses_per_month": uses_per_month,
                "renewal_date": renewal_date,
                "importance": importance,
                "notes": notes,
            }
        )

    return pd.DataFrame(records)


def calculate_cost_per_use(monthly_cost: float, uses_per_month: int) -> float:
    if uses_per_month == 0:
        return money(monthly_cost)
    return money(monthly_cost / uses_per_month)


def score_subscription(row: pd.Series, today: date) -> int:
    score = 0

    if row["monthly_cost"] >= 40:
        score += 25
    elif row["monthly_cost"] >= 20:
        score += 15
    elif row["monthly_cost"] >= 10:
        score += 8

    if row["uses_per_month"] == 0:
        score += 35
    elif row["uses_per_month"] <= 2:
        score += 25
    elif row["uses_per_month"] <= 5:
        score += 12

    if row["cost_per_use"] >= 20:
        score += 25
    elif row["cost_per_use"] >= 10:
        score += 15
    elif row["cost_per_use"] >= 5:
        score += 8

    if row["days_until_renewal"] <= 7:
        score += 20
    elif row["days_until_renewal"] <= 14:
        score += 12
    elif row["days_until_renewal"] <= 30:
        score += 6

    if row["importance"] == "Low":
        score += 20
    elif row["importance"] == "Medium":
        score += 8

    return min(score, 100)


def risk_level(score: int) -> str:
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"


def recommendation(row: pd.Series) -> str:
    if row["risk_level"] == "High":
        return "Review before renewal"
    if row["uses_per_month"] == 0:
        return "Cancel if still unused"
    if row["cost_per_use"] >= 10:
        return "Check value per use"
    return "Keep watching"


def analyze_subscriptions(df: pd.DataFrame, today: date | None = None) -> pd.DataFrame:
    today = today or date.today()
    clean = clean_subscriptions(df)
    analyzed = clean.copy()

    analyzed["yearly_cost"] = analyzed["monthly_cost"].apply(lambda value: money(value * 12))
    analyzed["cost_per_use"] = analyzed.apply(
        lambda row: calculate_cost_per_use(row["monthly_cost"], row["uses_per_month"]), axis=1
    )
    analyzed["days_until_renewal"] = analyzed["renewal_date"].apply(lambda renewal: (renewal - today).days)
    analyzed["reality_score"] = analyzed.apply(lambda row: score_subscription(row, today), axis=1)
    analyzed["risk_level"] = analyzed["reality_score"].apply(risk_level)
    analyzed["recommendation"] = analyzed.apply(recommendation, axis=1)

    return analyzed.sort_values(
        ["reality_score", "monthly_cost", "name"], ascending=[False, False, True]
    ).reset_index(drop=True)


def summarize_spend(analyzed: pd.DataFrame) -> dict[str, float | int]:
    total_monthly = money(analyzed["monthly_cost"].sum())
    total_yearly = money(total_monthly * 12)
    average_cost_per_use = 0.0
    active_uses = analyzed[analyzed["uses_per_month"] > 0]

    if not active_uses.empty:
        average_cost_per_use = money(active_uses["cost_per_use"].mean())

    return {
        "subscription_count": int(len(analyzed)),
        "total_monthly": total_monthly,
        "total_yearly": total_yearly,
        "average_cost_per_use": average_cost_per_use,
        "high_risk_count": int((analyzed["risk_level"] == "High").sum()),
    }


def category_spend(analyzed: pd.DataFrame) -> pd.DataFrame:
    grouped = analyzed.groupby("category", as_index=False)["monthly_cost"].sum()
    grouped["yearly_cost"] = grouped["monthly_cost"].apply(lambda value: money(value * 12))
    grouped["monthly_cost"] = grouped["monthly_cost"].apply(money)
    return grouped.sort_values("monthly_cost", ascending=False).reset_index(drop=True)


def run_savings_scenario(analyzed: pd.DataFrame, removed_names: list[str]) -> ScenarioResult:
    removed = tuple(sorted(set(removed_names)))
    current_monthly = money(analyzed["monthly_cost"].sum())
    remaining = analyzed[~analyzed["name"].isin(removed)]
    new_monthly = money(remaining["monthly_cost"].sum())
    monthly_savings = money(current_monthly - new_monthly)

    return ScenarioResult(
        removed_names=removed,
        current_monthly=current_monthly,
        new_monthly=new_monthly,
        monthly_savings=monthly_savings,
        current_yearly=money(current_monthly * 12),
        new_yearly=money(new_monthly * 12),
        yearly_savings=money(monthly_savings * 12),
    )


def export_action_plan(analyzed: pd.DataFrame, removed_names: list[str]) -> str:
    scenario = analyzed[analyzed["name"].isin(removed_names)].copy()
    if scenario.empty:
        scenario = analyzed.head(0).copy()
    export = scenario.reindex(columns=EXPORT_COLUMNS)
    return export.to_csv(index=False)
