"""Tax bracket calculations for Quebec residents, 2026."""

from .tax_config import (
    FEDERAL_BRACKETS_2026,
    FEDERAL_BPA_2026,
    QUEBEC_BRACKETS_2026,
    QUEBEC_BPA_2026,
    QUEBEC_ABATEMENT,
    OAS_CLAWBACK_THRESHOLD_2026,
    OAS_CLAWBACK_RATE,
    OAS_MINIMUM_AGE,
    OAS_MAX_ANNUAL_65_74,
    OAS_MAX_ANNUAL_75_PLUS,
    Bracket,
)


def bracket_tax(income: float, brackets: Bracket) -> float:
    """
    Compute progressive (marginal) tax on *income* using the supplied brackets.

    Each bracket is (upper_bound, rate).  The rate applies to the slice of
    income between the previous upper bound and the current one.

    Args:
        income:   Taxable income (non-negative).
        brackets: List of (upper_bound, rate) in ascending order; last entry
                  must have upper_bound == float("inf").

    Returns:
        Tax owing (float).
    """
    if income <= 0:
        return 0.0

    tax = 0.0
    prev_limit = 0.0
    for upper, rate in brackets:
        if income <= prev_limit:
            break
        taxable_slice = min(income, upper) - prev_limit
        tax += taxable_slice * rate
        prev_limit = upper

    return tax


def _bpa_credit(bpa: float, brackets: Bracket) -> float:
    """Return the non-refundable basic personal amount credit."""
    return bracket_tax(bpa, brackets)


def federal_tax(taxable_income: float) -> float:
    """
    Federal income tax for a Quebec resident, 2026.

    Applies:
      - Progressive federal brackets
      - Basic Personal Amount non-refundable credit (bottom-bracket rate × BPA)
      - 16.5% Quebec Abatement

    Args:
        taxable_income: Total federal taxable income.

    Returns:
        Federal tax after BPA credit and Quebec Abatement (≥ 0).
    """
    gross = bracket_tax(taxable_income, FEDERAL_BRACKETS_2026)
    bpa_credit = _bpa_credit(FEDERAL_BPA_2026, FEDERAL_BRACKETS_2026)
    net = max(0.0, gross - bpa_credit)
    return net * (1.0 - QUEBEC_ABATEMENT)


def provincial_tax(taxable_income: float) -> float:
    """
    Quebec provincial income tax, 2026.

    Applies:
      - Progressive Quebec brackets
      - Quebec Basic Personal Amount non-refundable credit

    Args:
        taxable_income: Total Quebec taxable income.

    Returns:
        Provincial tax after BPA credit (≥ 0).
    """
    gross = bracket_tax(taxable_income, QUEBEC_BRACKETS_2026)
    bpa_credit = _bpa_credit(QUEBEC_BPA_2026, QUEBEC_BRACKETS_2026)
    return max(0.0, gross - bpa_credit)


def combined_tax(taxable_income: float) -> float:
    """Federal (post-abatement) + provincial tax combined."""
    return federal_tax(taxable_income) + provincial_tax(taxable_income)


def marginal_tax_on_income(base_income: float, additional_income: float) -> dict:
    """
    Compute the marginal federal + provincial tax attributable to additional
    income stacked on top of base_income.

    Returns a dict with keys: federal, provincial, total.
    """
    fed_base = federal_tax(base_income)
    fed_total = federal_tax(base_income + additional_income)
    prov_base = provincial_tax(base_income)
    prov_total = provincial_tax(base_income + additional_income)

    return {
        "federal": max(0.0, fed_total - fed_base),
        "provincial": max(0.0, prov_total - prov_base),
        "total": max(0.0, (fed_total + prov_total) - (fed_base + prov_base)),
    }


def compute_oas_clawback(base_income: float, additional_income: float, age: int) -> float:
    """
    Compute the OAS Recovery Tax ("clawback") attributable to the disposition.

    The CRA requires OAS recipients to repay 15 cents of benefit for every
    dollar of net income above the annual threshold, up to the full benefit
    received.  The clawback is triggered only for taxpayers aged 65+.

    This function calculates the incremental clawback caused by stacking the
    disposition income on top of the seller's other annual income.

    Args:
        base_income:       Other annual taxable income before the disposition.
        additional_income: Extra income from the disposition (recapture + taxable CG).
        age:               Seller's age at time of sale.

    Returns:
        OAS clawback amount in CAD (≥ 0).
    """
    if age < OAS_MINIMUM_AGE:
        return 0.0
    max_oas = OAS_MAX_ANNUAL_75_PLUS if age >= 75 else OAS_MAX_ANNUAL_65_74
    total_income = base_income + additional_income
    # Clawback on total income above threshold, minus any clawback already
    # incurred on base income alone (so we return only the incremental portion)
    clawback_on_total = min(max_oas, max(0.0, total_income - OAS_CLAWBACK_THRESHOLD_2026) * OAS_CLAWBACK_RATE)
    clawback_on_base = min(max_oas, max(0.0, base_income - OAS_CLAWBACK_THRESHOLD_2026) * OAS_CLAWBACK_RATE)
    return max(0.0, clawback_on_total - clawback_on_base)
