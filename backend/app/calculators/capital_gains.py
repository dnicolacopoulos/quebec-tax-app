"""Capital gains calculations with deemed disposition and principal residence support."""

from __future__ import annotations
from typing import Optional
from .tax_config import CAPITAL_GAINS_INCLUSION


def compute_acb(inherited: bool, fmv_at_death: Optional[float], user_acb: Optional[float]) -> float:
    """
    Return the Adjusted Cost Base.

    If inherited, ACB resets to FMV at date of death (deemed disposition).
    Otherwise, return the user-supplied ACB.
    """
    if inherited:
        if fmv_at_death is None or fmv_at_death <= 0:
            raise ValueError("FMV at death must be provided and positive for inherited property.")
        return fmv_at_death
    if user_acb is None or user_acb < 0:
        raise ValueError("ACB must be provided and non-negative for non-inherited property.")
    return user_acb


def compute_capital_gain(
    sale_price: float,
    acb: float,
    selling_costs: float,
    cca_claimed: bool,
    original_cost: Optional[float],
) -> float:
    """
    Compute the capital gain on disposition.

    When CCA was claimed:
      - The effective cost base for capital gain purposes is max(ACB, original_cost)
        because recapture brings the UCC back up to original_cost first.
      - Capital gain = proceeds of disposition - max(ACB, original_cost) - selling_costs

    When no CCA:
      - Capital gain = proceeds - ACB - selling_costs

    Returns the capital gain (may be 0 if ACB >= proceeds).
    """
    net_proceeds = sale_price - selling_costs
    if cca_claimed and original_cost is not None:
        effective_acb = max(acb, original_cost)
    else:
        effective_acb = acb
    return max(0.0, net_proceeds - effective_acb)


def compute_pre_exempt_fraction(
    years_principal_residence: int,
    years_owned: int,
    pre_use_pct: float = 100.0,
) -> float:
    """
    Compute the fraction of the capital gain exempt under the
    Principal Residence Exemption (PRE).

    CRA formula:
        time_fraction  = min(1, (1 + years_pr) / years_owned)
        space_fraction = pre_use_pct / 100
        exempt fraction = time_fraction × space_fraction

    The "+1" bonus year is a statutory allowance.
    pre_use_pct < 100 applies to partial-use properties (e.g. a duplex where
    one unit — say 40% of the building — was the taxpayer's principal residence).

    Args:
        years_principal_residence: Years the property was designated as PR.
        years_owned:               Total years the property was owned.
        pre_use_pct:               Percentage of the property used as principal
                                   residence (0–100). Defaults to 100.

    Returns:
        Exempt fraction in [0.0, 1.0].
    """
    if years_owned <= 0 or years_principal_residence < 0 or pre_use_pct <= 0:
        return 0.0
    time_fraction = min(1.0, (1 + years_principal_residence) / years_owned)
    space_fraction = min(1.0, pre_use_pct / 100.0)
    return time_fraction * space_fraction


def compute_taxable_capital_gain(
    capital_gain: float,
    pre_exempt_fraction: float = 0.0,
) -> float:
    """
    Return the taxable (includible) portion of a capital gain after applying
    the Principal Residence Exemption and the 50% inclusion rate.

    The PRE shelters the exempt fraction of the gain entirely; only the
    remaining (non-exempt) portion is subject to the inclusion rate.

    Note: CCA recapture is NOT sheltered by the PRE — it is handled separately
    and is always 100% taxable income.

    Args:
        capital_gain:        Total capital gain before PRE.
        pre_exempt_fraction: Fraction of the gain exempt under PRE (0.0–1.0).

    Returns:
        Taxable capital gain after PRE and 50% inclusion.
    """
    taxable_gain = capital_gain * max(0.0, 1.0 - pre_exempt_fraction)
    return taxable_gain * CAPITAL_GAINS_INCLUSION
