"""
CCA (Capital Cost Allowance) recapture and terminal loss calculations.

CCA recapture is 100% taxable as ordinary income — it is NOT a capital gain.
Terminal loss is fully deductible against ordinary income.
"""


def compute_recapture(
    sale_price: float,
    original_cost: float,
    ucc: float,
) -> float:
    """
    Compute CCA recapture.

    Recapture occurs when the proceeds (capped at original cost) exceed UCC.
    The full recapture amount is added to ordinary income — not treated as a
    capital gain.

    Formula:  recapture = min(sale_price, original_cost) - ucc
              (only if positive)

    Args:
        sale_price:    Gross sale price of the property.
        original_cost: Original depreciable cost (not ACB) of the property.
        ucc:           Undepreciated Capital Cost at time of sale.

    Returns:
        Recapture amount (≥ 0). Zero if there is no recapture.
    """
    proceeds_for_recapture = min(sale_price, original_cost)
    return max(0.0, proceeds_for_recapture - ucc)


def compute_terminal_loss(
    sale_price: float,
    original_cost: float,
    ucc: float,
) -> float:
    """
    Compute terminal loss (fully deductible against ordinary income).

    Terminal loss = UCC - min(sale_price, original_cost), when positive.

    Args:
        sale_price:    Gross sale price.
        original_cost: Original depreciable cost.
        ucc:           Undepreciated Capital Cost at time of sale.

    Returns:
        Terminal loss amount (≥ 0). Zero if there is no terminal loss.
    """
    proceeds_for_recapture = min(sale_price, original_cost)
    return max(0.0, ucc - proceeds_for_recapture)
