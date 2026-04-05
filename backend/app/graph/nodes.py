"""
LangGraph node functions for the property wizard.

Each node either:
  (a) returns the next Question to present to the user, stored in state["step"], or
  (b) performs the calculation and stores the result in state["result"].

Nodes mutate and return the state dict.
"""

from __future__ import annotations
from typing import Optional
from app.models.schemas import Question
from app.graph.state import PropertyState
from app.calculators.capital_gains import (
    compute_acb,
    compute_capital_gain,
    compute_pre_exempt_fraction,
    compute_taxable_capital_gain,
)
from app.calculators.cca import compute_recapture, compute_terminal_loss
from app.calculators.tax import marginal_tax_on_income, compute_oas_clawback
from app.calculators.keep_scenario import project_keep
from app.calculators.sell_scenario import project_sell


# ---------------------------------------------------------------------------
# Question definitions (keyed by step name)
# ---------------------------------------------------------------------------

QUESTIONS: dict[str, Question] = {
    "inherited": Question(
        key="inherited",
        text="Was this property inherited?",
        type="yesno",
    ),
    "fmv_at_death": Question(
        key="fmv_at_death",
        text="What was the Fair Market Value (FMV) of the property at the date of death?",
        type="currency",
        hint="This becomes the Adjusted Cost Base (deemed disposition rule).",
    ),
    "user_acb": Question(
        key="user_acb",
        text="What is your Adjusted Cost Base (ACB) for the property?",
        type="currency",
        hint="Original purchase price plus capital improvements.",
    ),
    "sale_price": Question(
        key="sale_price",
        text="What is the expected sale price?",
        type="currency",
    ),
    "selling_costs_pct": Question(
        key="selling_costs_pct",
        text="Estimated selling costs (notary, real-estate commission, etc.) as a percentage of sale price?",
        type="percentage",
        default=5.0,
        hint="Typically 4–7%. Defaults to 5%.",
    ),
    "principal_residence": Question(
        key="principal_residence",
        text="Was this property ever your principal residence?",
        type="yesno",
        hint="If yes, part or all of the capital gain may be tax-exempt.",
    ),
    "years_principal_residence": Question(
        key="years_principal_residence",
        text="How many years was it designated as your principal residence?",
        type="number",
        hint="Count only years you ordinarily inhabited it as your main home.",
    ),
    "years_owned": Question(
        key="years_owned",
        text="How many years have you owned the property in total?",
        type="number",
    ),
    "pre_use_pct": Question(
        key="pre_use_pct",
        text="What percentage of the property was used as your principal residence?",
        type="percentage",
        default=100.0,
        hint="Use 100% if the entire property was your home. For a duplex where you occupied one unit, enter the portion (e.g. 40 for 40%).",
    ),
    "cca_claimed": Question(
        key="cca_claimed",
        text="Have you ever claimed Capital Cost Allowance (CCA / depreciation) on this property?",
        type="yesno",
    ),
    "original_cost": Question(
        key="original_cost",
        text="What was the original depreciable cost of the building (not land)?",
        type="currency",
        hint="Usually the purchase price allocated to the building portion.",
    ),
    "ucc": Question(
        key="ucc",
        text="What is the current Undepreciated Capital Cost (UCC)?",
        type="currency",
        hint="Check your most recent T776 / TP-128. Lower UCC = more potential recapture.",
    ),
    "monthly_gross_rent": Question(
        key="monthly_gross_rent",
        text="What is the current monthly gross rental income?",
        type="currency",
    ),
    "monthly_expenses": Question(
        key="monthly_expenses",
        text="What are the monthly operating expenses (insurance, maintenance, property tax, etc.)?",
        type="currency",
        hint="Exclude mortgage payments — those are entered separately.",
    ),
    "has_mortgage": Question(
        key="has_mortgage",
        text="Is there an outstanding mortgage on this property?",
        type="yesno",
    ),
    "mortgage_balance": Question(
        key="mortgage_balance",
        text="What is the current outstanding mortgage balance?",
        type="currency",
    ),
    "mortgage_annual_rate": Question(
        key="mortgage_annual_rate",
        text="What is the mortgage interest rate?",
        type="percentage",
        hint="Enter as a percentage, e.g. 4.5 for 4.5%.",
    ),
    "mortgage_months_remaining": Question(
        key="mortgage_months_remaining",
        text="How many months remain on the mortgage amortization?",
        type="number",
        hint="E.g. 240 for 20 years remaining.",
    ),
    "other_annual_income": Question(
        key="other_annual_income",
        text="What is your other annual taxable income (employment, pension, etc.), excluding this property?",
        type="currency",
        default=0.0,
        hint="Used to determine your marginal tax bracket.",
    ),
    "seller_age": Question(
        key="seller_age",
        text="What is the seller's age?",
        type="number",
        default=0,
        hint="OAS clawback (15% recovery tax) applies if age is 65 or older and net income exceeds the annual threshold.",
    ),
}


# ---------------------------------------------------------------------------
# Node functions
# ---------------------------------------------------------------------------


def node_ask_inherited(state: dict) -> dict:
    state["step"] = "inherited"
    return state


def node_ask_fmv_at_death(state: dict) -> dict:
    state["step"] = "fmv_at_death"
    return state


def node_ask_user_acb(state: dict) -> dict:
    state["step"] = "user_acb"
    return state


def node_ask_sale_price(state: dict) -> dict:
    state["step"] = "sale_price"
    return state


def node_ask_selling_costs_pct(state: dict) -> dict:
    state["step"] = "selling_costs_pct"
    return state


def node_ask_cca_claimed(state: dict) -> dict:
    state["step"] = "cca_claimed"
    return state


def node_ask_original_cost(state: dict) -> dict:
    state["step"] = "original_cost"
    return state


def node_ask_ucc(state: dict) -> dict:
    state["step"] = "ucc"
    return state


def node_ask_monthly_gross_rent(state: dict) -> dict:
    state["step"] = "monthly_gross_rent"
    return state


def node_ask_monthly_expenses(state: dict) -> dict:
    state["step"] = "monthly_expenses"
    return state


def node_ask_has_mortgage(state: dict) -> dict:
    state["step"] = "has_mortgage"
    return state


def node_ask_mortgage_balance(state: dict) -> dict:
    state["step"] = "mortgage_balance"
    return state


def node_ask_mortgage_annual_rate(state: dict) -> dict:
    state["step"] = "mortgage_annual_rate"
    return state


def node_ask_mortgage_months_remaining(state: dict) -> dict:
    state["step"] = "mortgage_months_remaining"
    return state


def node_ask_other_annual_income(state: dict) -> dict:
    state["step"] = "other_annual_income"
    return state


def node_calculate(state: PropertyState) -> PropertyState:
    """
    Run all calculations and store the result in state["result"].
    """
    s = state

    # ACB
    acb = compute_acb(
        inherited=s.get("inherited") or False,
        fmv_at_death=s.get("fmv_at_death"),
        user_acb=s.get("user_acb"),
    )

    sale_price = s.get("sale_price") or 0.0
    selling_costs_pct = s.get("selling_costs_pct") or 5.0
    selling_costs = sale_price * (selling_costs_pct / 100.0)

    cca_claimed = s.get("cca_claimed") or False
    original_cost: Optional[float] = s.get("original_cost")
    ucc: Optional[float] = s.get("ucc")
    other_income = s.get("other_annual_income") or 0.0

    # CCA recapture / terminal loss
    recapture = 0.0
    terminal_loss = 0.0
    if cca_claimed and original_cost is not None and ucc is not None:
        recapture = compute_recapture(sale_price, original_cost, ucc)
        terminal_loss = compute_terminal_loss(sale_price, original_cost, ucc)

    # Capital gain
    capital_gain = compute_capital_gain(
        sale_price=sale_price,
        acb=acb,
        selling_costs=selling_costs,
        cca_claimed=cca_claimed,
        original_cost=original_cost,
    )

    # Principal Residence Exemption (shelters capital gain only — not recapture)
    pre_exempt_fraction = 0.0
    if s.get("principal_residence"):
        years_pr = s.get("years_principal_residence") or 0
        years_owned = s.get("years_owned") or 0
        pre_use_pct: float = float(s.get("pre_use_pct") or 100.0)
        pre_exempt_fraction = compute_pre_exempt_fraction(years_pr, years_owned, pre_use_pct)
    pre_exempt_gain = round(capital_gain * pre_exempt_fraction, 2)

    taxable_cg = compute_taxable_capital_gain(capital_gain, pre_exempt_fraction)

    # Total additional taxable income stacked on other_income
    # Recapture is 100% income; capital gain uses 50% inclusion
    taxable_additional = recapture + taxable_cg - terminal_loss
    tax_breakdown_raw = marginal_tax_on_income(other_income, max(0.0, taxable_additional))

    # OAS clawback — applies only if seller is 65+
    seller_age = s.get("seller_age") or 0
    oas_clawback = compute_oas_clawback(other_income, max(0.0, taxable_additional), seller_age)

    total_tax = tax_breakdown_raw["total"] + oas_clawback

    has_mortgage = s.get("has_mortgage") or False
    mortgage_balance = (s.get("mortgage_balance") or 0.0) if has_mortgage else 0.0
    mortgage_annual_rate = ((s.get("mortgage_annual_rate") or 0.0) / 100.0) if has_mortgage else 0.0
    mortgage_months_remaining = (s.get("mortgage_months_remaining") or 0) if has_mortgage else 0

    sell_net_proceeds = max(0.0, sale_price - selling_costs - mortgage_balance - total_tax)

    # Projections
    sell_series = project_sell(sell_net_proceeds)
    keep_series = project_keep(
        sale_price=sale_price,
        monthly_gross_rent=s.get("monthly_gross_rent") or 0.0,
        monthly_expenses=s.get("monthly_expenses") or 0.0,
        other_annual_income=other_income,
        has_mortgage=has_mortgage,
        mortgage_balance=mortgage_balance,
        mortgage_annual_rate=mortgage_annual_rate,
        mortgage_months_remaining=mortgage_months_remaining,
    )

    sell_year_10 = sell_series[-1]["value"]
    keep_year_10 = keep_series[-1]
    keep_total_year_10 = keep_year_10["total"]

    delta = sell_year_10 - keep_total_year_10
    if abs(delta) < 0.01 * max(sell_year_10, keep_total_year_10, 1):
        recommendation = "similar"
    elif delta > 0:
        recommendation = "sell"
    else:
        recommendation = "keep"

    state["result"] = {
        "summary": {
            "selling_costs": round(selling_costs, 2),
            "tax_breakdown": {
                "recapture_income": round(recapture, 2),
                "capital_gain": round(capital_gain, 2),
                "pre_exempt_gain": pre_exempt_gain,
                "taxable_capital_gain": round(taxable_cg, 2),
                "federal_tax": round(tax_breakdown_raw["federal"], 2),
                "provincial_tax": round(tax_breakdown_raw["provincial"], 2),
                "oas_clawback": round(oas_clawback, 2),
                "total_tax": round(total_tax, 2),
            },
            "sell_net_proceeds": round(sell_net_proceeds, 2),
            "sell_year_10": round(sell_year_10, 2),
            "keep_equity_year_10": round(keep_year_10["equity"], 2),
            "keep_cumulative_cf_year_10": round(keep_year_10["cumulative_cash_flow"], 2),
            "keep_total_year_10": round(keep_total_year_10, 2),
            "recommendation": recommendation,
            "recommendation_delta": round(abs(delta), 2),
        },
        "sell_series": sell_series,
        "keep_series": keep_series,
    }

    state["step"] = "done"
    return state
