"""
Keep & Rent scenario: 10-year projection.

Assumptions:
  - Property appreciates at 3% per year (PROPERTY_APPRECIATION_RATE).
  - Only the interest portion of the mortgage payment is deductible against
    rental income for tax purposes; principal repayment is not deductible.
  - Net operating expenses (excluding mortgage) are fully deductible.
  - Tax on rental income is computed as marginal tax stacked on other_income.
"""

from __future__ import annotations
from .tax_config import PROPERTY_APPRECIATION_RATE, PROJECTION_YEARS
from .tax import marginal_tax_on_income


def monthly_payment(principal: float, annual_rate: float, months: int) -> float:
    """
    Standard amortizing mortgage monthly payment.

    Args:
        principal:   Outstanding mortgage balance.
        annual_rate: Annual interest rate as a decimal (e.g. 0.05 for 5%).
        months:      Number of months remaining in amortization.

    Returns:
        Monthly payment amount.
    """
    if months <= 0 or principal <= 0:
        return 0.0
    if annual_rate == 0:
        return principal / months
    r = annual_rate / 12.0
    return principal * r * (1 + r) ** months / ((1 + r) ** months - 1)


def _amortize_one_year(
    balance: float,
    annual_rate: float,
    payment: float,
) -> "tuple[float, float, float]":
    """
    Run 12 months of amortization.

    Returns:
        (new_balance, annual_interest_paid, annual_principal_paid)
    """
    annual_interest = 0.0
    annual_principal = 0.0
    r = annual_rate / 12.0

    for _ in range(12):
        if balance <= 0:
            break
        interest = balance * r
        principal_portion = min(payment - interest, balance)
        annual_interest += interest
        annual_principal += principal_portion
        balance = max(0.0, balance - principal_portion)

    return balance, annual_interest, annual_principal


def project_keep(
    sale_price: float,
    monthly_gross_rent: float,
    monthly_expenses: float,
    other_annual_income: float,
    has_mortgage: bool,
    mortgage_balance: float,
    mortgage_annual_rate: float,
    mortgage_months_remaining: int,
) -> list[dict]:
    """
    Project the Keep & Rent scenario over PROJECTION_YEARS years.

    Each year dict contains:
      - year:                  int
      - property_value:        float  (FMV at end of year)
      - mortgage_balance:      float  (remaining balance at end of year)
      - equity:                float  (property_value - mortgage_balance)
      - annual_cash_flow:      float  (after-tax cash flow for the year)
      - cumulative_cash_flow:  float  (sum of after-tax cash flows to date)
      - total:                 float  (equity + cumulative_cash_flow)
    """
    payment = (
        monthly_payment(
            mortgage_balance, mortgage_annual_rate, mortgage_months_remaining
        )
        if has_mortgage
        else 0.0
    )

    balance = mortgage_balance if has_mortgage else 0.0
    property_value = sale_price  # current FMV is the would-be sale price
    cumulative_cf = 0.0
    results = []

    for year in range(1, PROJECTION_YEARS + 1):
        # --- mortgage amortization for this year ---
        if has_mortgage and balance > 0:
            balance, annual_interest, _ = _amortize_one_year(
                balance, mortgage_annual_rate, payment
            )
        else:
            annual_interest = 0.0

        # --- rental income tax ---
        gross_rent_annual = monthly_gross_rent * 12
        expenses_annual = monthly_expenses * 12
        # Taxable rental income = gross rent - operating expenses - mortgage interest
        taxable_rental = max(0.0, gross_rent_annual - expenses_annual - annual_interest)
        rental_tax = marginal_tax_on_income(other_annual_income, taxable_rental)[
            "total"
        ]

        # --- after-tax cash flow ---
        mortgage_payments_annual = payment * 12
        annual_cf = (
            gross_rent_annual - expenses_annual - mortgage_payments_annual - rental_tax
        )
        cumulative_cf += annual_cf

        # --- property value ---
        property_value = sale_price * (1 + PROPERTY_APPRECIATION_RATE) ** year

        equity = max(0.0, property_value - balance)

        results.append(
            {
                "year": year,
                "property_value": round(property_value, 2),
                "mortgage_balance": round(max(0.0, balance), 2),
                "equity": round(equity, 2),
                "annual_cash_flow": round(annual_cf, 2),
                "cumulative_cash_flow": round(cumulative_cf, 2),
                "total": round(equity + cumulative_cf, 2),
            }
        )

    return results
