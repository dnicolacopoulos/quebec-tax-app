"""LangGraph state definition for the property wizard."""

from __future__ import annotations
from typing import Any, TypedDict


class PropertyState(TypedDict, total=False):
    # ---- navigation ----
    step: str  # name of the current node
    history: list[dict[str, Any]]  # [{role, text}] rendered in chat

    # ---- property inputs ----
    inherited: bool | None
    fmv_at_death: float | None
    user_acb: float | None
    sale_price: float | None
    selling_costs_pct: float | None  # percentage, e.g. 5.0

    # ---- CCA ----
    cca_claimed: bool | None
    ucc: float | None
    original_cost: float | None

    # ---- rental ----
    monthly_gross_rent: float | None
    monthly_expenses: float | None

    # ---- mortgage ----
    has_mortgage: bool | None
    mortgage_balance: float | None
    mortgage_annual_rate: float | None  # decimal, e.g. 0.05
    mortgage_months_remaining: int | None

    # ---- other income ----
    other_annual_income: float | None

    # ---- output ----
    result: dict[str, Any] | None
