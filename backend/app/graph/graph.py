"""
LangGraph StateGraph for the property wizard.

The graph drives a step-by-step wizard; transitions are conditional based on
answers (inherited? → fmv vs acb; cca_claimed? → ucc/cost; has_mortgage? → loan details).

Since this is a pure structured wizard (no LLM), the graph is invoked one
step at a time from the FastAPI session store — we do NOT stream or compile
to a runnable in the traditional LangGraph way. Instead, graph.py exposes:

    next_node(state) -> str   — given current state, return what step comes next.

The FastAPI routes call the appropriate node function from nodes.py directly.
"""

from __future__ import annotations

from app.graph.state import PropertyState


# ---------------------------------------------------------------------------
# Step ordering / routing
# ---------------------------------------------------------------------------


def next_step(state: PropertyState) -> str:
    """
    Pure function: given the current state, return the name of the next step.

    "done" means calculation is complete.
    """
    step = state.get("step", "")

    if step == "":
        return "inherited"

    if step == "inherited":
        return "fmv_at_death" if state.get("inherited") else "user_acb"

    if step in ("fmv_at_death", "user_acb"):
        return "sale_price"

    if step == "sale_price":
        return "selling_costs_pct"

    if step == "selling_costs_pct":
        return "cca_claimed"

    if step == "cca_claimed":
        return "original_cost" if state.get("cca_claimed") else "monthly_gross_rent"

    if step == "original_cost":
        return "ucc"

    if step == "ucc":
        return "monthly_gross_rent"

    if step == "monthly_gross_rent":
        return "monthly_expenses"

    if step == "monthly_expenses":
        return "has_mortgage"

    if step == "has_mortgage":
        return (
            "mortgage_balance" if state.get("has_mortgage") else "other_annual_income"
        )

    if step == "mortgage_balance":
        return "mortgage_annual_rate"

    if step == "mortgage_annual_rate":
        return "mortgage_months_remaining"

    if step == "mortgage_months_remaining":
        return "other_annual_income"

    if step == "other_annual_income":
        return "calculate"

    return "done"
