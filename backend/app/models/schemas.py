"""Pydantic request/response models shared across routes and graph."""

from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Literal, Optional


# ---------------------------------------------------------------------------
# API I/O
# ---------------------------------------------------------------------------


class AnswerRequest(BaseModel):
    value: Any = Field(..., description="The user's answer to the current question.")


class CalculateRequest(BaseModel):
    inherited: bool = False
    fmv_at_death: Optional[float] = None
    user_acb: Optional[float] = None
    sale_price: float
    selling_costs_pct: float = 5.0
    cca_claimed: bool = False
    original_cost: Optional[float] = None
    ucc: Optional[float] = None
    monthly_gross_rent: float
    monthly_expenses: float
    has_mortgage: bool = False
    mortgage_balance: Optional[float] = None
    mortgage_annual_rate: Optional[float] = None
    mortgage_months_remaining: Optional[int] = None
    other_annual_income: float = 0.0
    seller_age: int = 0
    principal_residence: bool = False
    pre_use_pct: float = 100.0
    years_principal_residence: Optional[int] = None
    years_owned: Optional[int] = None


class Question(BaseModel):
    key: str
    text: str
    type: Literal["currency", "number", "percentage", "yesno"]
    default: Optional[Any] = None
    hint: Optional[str] = None


# ---------------------------------------------------------------------------
# Calculation result
# ---------------------------------------------------------------------------


class TaxBreakdown(BaseModel):
    recapture_income: float
    capital_gain: float
    pre_exempt_gain: float          # portion of capital gain sheltered by PRE
    taxable_capital_gain: float     # after PRE + 50% inclusion
    federal_tax: float
    provincial_tax: float
    oas_clawback: float             # incremental OAS recovery tax (0 if age < 65)
    total_tax: float


class SellYearPoint(BaseModel):
    year: int
    value: float


class KeepYearPoint(BaseModel):
    year: int
    property_value: float
    mortgage_balance: float
    equity: float
    annual_cash_flow: float
    cumulative_cash_flow: float
    total: float


class ResultSummary(BaseModel):
    selling_costs: float
    tax_breakdown: TaxBreakdown
    sell_net_proceeds: float
    sell_year_10: float
    keep_equity_year_10: float
    keep_cumulative_cf_year_10: float
    keep_total_year_10: float
    recommendation: Literal["sell", "keep", "similar"]
    recommendation_delta: float  # absolute difference in favour of recommendation


class CalculationResult(BaseModel):
    summary: ResultSummary
    sell_series: list[SellYearPoint]
    keep_series: list[KeepYearPoint]


# ---------------------------------------------------------------------------
# Session responses
# ---------------------------------------------------------------------------


class SessionCreatedResponse(BaseModel):
    session_id: str
    question: Question


class AnswerResponse(BaseModel):
    question: Optional[Question] = None
    result: Optional[CalculationResult] = None
