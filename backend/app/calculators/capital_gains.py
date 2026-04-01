"""Capital gains calculations with deemed disposition support."""

from __future__ import annotations
from typing import Optional
from .tax_config import CAPITAL_GAINS_INCLUSION


def compute_acb(
    inherited: bool, fmv_at_death: Optional[float], user_acb: Optional[float]
) -> float:
    """
    Return the Adjusted Cost Base.

    If inherited, ACB resets to FMV at date of death (deemed disposition).
    Otherwise, return the user-supplied ACB.
    """
    if inherited:
        if fmv_at_death is None or fmv_at_death <= 0:
            raise ValueError(
                "FMV at death must be provided and positive for inherited property."
            )
        return fmv_at_death
    if user_acb is None or user_acb < 0:
        raise ValueError(
            "ACB must be provided and non-negative for non-inherited property."
        )
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


def compute_taxable_capital_gain(capital_gain: float) -> float:
    """Return the taxable (includible) portion of a capital gain."""
    return capital_gain * CAPITAL_GAINS_INCLUSION
