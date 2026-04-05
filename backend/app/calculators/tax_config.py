"""
2026 Quebec & Federal tax constants.

Sources:
  Federal brackets: https://www.canada.ca/en/revenue-agency/services/tax/individuals/
                    frequently-asked-questions-individuals/canadian-income-tax-rates-individuals-current-previous-years.html
                    (Date modified: 2026-01-20)
  Quebec brackets:  https://www.revenuquebec.ca/en/citizens/income-tax-return/
                    completing-your-income-tax-return/income-tax-rates/
                    (Inflation-indexed from 2025 published values)

LAST_VERIFIED: 2026-03-31
"""

from typing import List, Tuple

# ---------------------------------------------------------------------------
# Type alias: list of (upper_bound, rate) pairs in ascending order.
# The last entry's upper_bound is float("inf") (top bracket).
# ---------------------------------------------------------------------------
Bracket = List[Tuple[float, float]]

# ---------------------------------------------------------------------------
# Federal 2026
# Note: bottom rate reduced from 15% → 14% effective July 1, 2025
#       (Royal Assent received March 2026).
# ---------------------------------------------------------------------------
FEDERAL_BRACKETS_2026: Bracket = [
    (58_523.00, 0.14),
    (117_045.00, 0.205),
    (181_440.00, 0.26),
    (258_482.00, 0.29),
    (float("inf"), 0.33),
]

# Federal Basic Personal Amount 2026
FEDERAL_BPA_2026: float = 16_129.00

# ---------------------------------------------------------------------------
# Quebec provincial 2026 (inflation-indexed from 2025 published thresholds)
# ---------------------------------------------------------------------------
QUEBEC_BRACKETS_2026: Bracket = [
    (54_295.00, 0.14),
    (108_570.00, 0.19),
    (132_000.00, 0.24),
    (float("inf"), 0.2575),
]

# Quebec Basic Personal Amount 2026
QUEBEC_BPA_2026: float = 17_183.00

# ---------------------------------------------------------------------------
# Immutable legislative constants — never overridden by any external source
# ---------------------------------------------------------------------------

# 50% inclusion rate confirmed; 66.7% proposal was voided.
CAPITAL_GAINS_INCLUSION: float = 0.50

# Quebec Abatement: reduces federal tax payable by 16.5% for Quebec residents
# because Quebec operates its own provincial tax system independently.
QUEBEC_ABATEMENT: float = 0.165

# ---------------------------------------------------------------------------
# OAS Recovery Tax ("clawback") — 2026 estimates
# The annual threshold is indexed to CPI each year; values below are
# approximate for the 2026 income year pending CRA confirmation.
# ---------------------------------------------------------------------------

# Net-income threshold above which OAS repayment begins (2026 estimate)
OAS_CLAWBACK_THRESHOLD_2026: float = 93_454.00

# Rate at which OAS is repaid on each dollar of income above the threshold
OAS_CLAWBACK_RATE: float = 0.15

# Minimum age for OAS eligibility (therefore clawback exposure)
OAS_MINIMUM_AGE: int = 65

# Maximum annual OAS benefit (approximate 2026 quarterly-indexed estimates)
OAS_MAX_ANNUAL_65_74: float = 8_732.00   # ~$727.67/month
OAS_MAX_ANNUAL_75_PLUS: float = 9_605.00  # ~$800.44/month (10% supplement, age 75+)

# Default property appreciation rate (Keep scenario)
PROPERTY_APPRECIATION_RATE: float = 0.03

# Default ETF annual return (Sell & Reinvest scenario, gross, no tax drag)
ETF_ANNUAL_RETURN: float = 0.07

# Projection horizon (years)
PROJECTION_YEARS: int = 10
