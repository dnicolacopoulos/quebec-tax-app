"""
Sell & Reinvest scenario: 10-year projection.

Assumptions:
  - Net sale proceeds (after tax, selling costs, mortgage payoff) are
    invested in a diversified ETF returning 7% per year (gross, no tax drag).
  - Returns compound annually.
"""

from .tax_config import ETF_ANNUAL_RETURN, PROJECTION_YEARS


def project_sell(net_proceeds: float) -> list[dict]:
    """
    Project invested net proceeds at ETF_ANNUAL_RETURN over PROJECTION_YEARS.

    Year 0 represents the initial invested amount (immediately post-sale).

    Each dict contains:
      - year:  int
      - value: float
    """
    results = [{"year": 0, "value": round(net_proceeds, 2)}]
    for year in range(1, PROJECTION_YEARS + 1):
        value = net_proceeds * (1 + ETF_ANNUAL_RETURN) ** year
        results.append({"year": year, "value": round(value, 2)})
    return results
