"""
Tests for app/calculators/sell_scenario.py and app/calculators/keep_scenario.py
"""

import pytest
from app.calculators.sell_scenario import project_sell
from app.calculators.keep_scenario import monthly_payment, project_keep
from app.calculators.tax_config import ETF_ANNUAL_RETURN, PROJECTION_YEARS


# ---------------------------------------------------------------------------
# project_sell
# ---------------------------------------------------------------------------


class TestProjectSell:
    def test_returns_eleven_entries(self):
        # Year 0 through PROJECTION_YEARS inclusive
        result = project_sell(100_000.0)
        assert len(result) == PROJECTION_YEARS + 1

    def test_year_0_equals_net_proceeds(self):
        result = project_sell(250_000.0)
        assert result[0] == {"year": 0, "value": 250_000.0}

    def test_compound_growth(self):
        net = 200_000.0
        result = project_sell(net)
        for entry in result:
            expected = round(net * (1 + ETF_ANNUAL_RETURN) ** entry["year"], 2)
            assert entry["value"] == pytest.approx(expected, rel=1e-4)

    def test_years_are_sequential(self):
        result = project_sell(100_000.0)
        assert [e["year"] for e in result] == list(range(PROJECTION_YEARS + 1))

    def test_values_are_non_decreasing(self):
        result = project_sell(150_000.0)
        values = [e["value"] for e in result]
        assert values == sorted(values)

    def test_zero_proceeds(self):
        result = project_sell(0.0)
        assert all(e["value"] == 0.0 for e in result)

    def test_year_10_value(self):
        net = 300_000.0
        result = project_sell(net)
        expected_y10 = round(net * (1 + ETF_ANNUAL_RETURN) ** 10, 2)
        assert result[10]["value"] == pytest.approx(expected_y10, rel=1e-4)


# ---------------------------------------------------------------------------
# monthly_payment
# ---------------------------------------------------------------------------


class TestMonthlyPayment:
    def test_standard_mortgage(self):
        # $400k at 5% over 25 years (300 months) — well-known formula
        payment = monthly_payment(400_000.0, 0.05, 300)
        # Expected ≈ $2,338.36
        assert payment == pytest.approx(2_338.36, rel=1e-3)

    def test_zero_balance(self):
        assert monthly_payment(0.0, 0.05, 300) == 0.0

    def test_zero_months(self):
        assert monthly_payment(400_000.0, 0.05, 0) == 0.0

    def test_zero_rate(self):
        # No interest → payment = principal / months
        assert monthly_payment(120_000.0, 0.0, 120) == pytest.approx(1_000.0)

    def test_payment_is_positive(self):
        assert monthly_payment(300_000.0, 0.045, 240) > 0.0


# ---------------------------------------------------------------------------
# project_keep
# ---------------------------------------------------------------------------


KEEP_BASE = dict(
    sale_price=500_000.0,
    monthly_gross_rent=2_500.0,
    monthly_expenses=500.0,
    other_annual_income=60_000.0,
    has_mortgage=False,
    mortgage_balance=0.0,
    mortgage_annual_rate=0.0,
    mortgage_months_remaining=0,
)


class TestProjectKeep:
    def test_returns_ten_entries(self):
        result = project_keep(**KEEP_BASE)
        assert len(result) == PROJECTION_YEARS

    def test_years_are_sequential(self):
        result = project_keep(**KEEP_BASE)
        assert [e["year"] for e in result] == list(range(1, PROJECTION_YEARS + 1))

    def test_keys_present(self):
        entry = project_keep(**KEEP_BASE)[0]
        required = {
            "year",
            "property_value",
            "mortgage_balance",
            "equity",
            "annual_cash_flow",
            "cumulative_cash_flow",
            "total",
        }
        assert required.issubset(entry.keys())

    def test_equity_equals_value_minus_balance_no_mortgage(self):
        result = project_keep(**KEEP_BASE)
        for entry in result:
            assert entry["equity"] == pytest.approx(entry["property_value"] - entry["mortgage_balance"], abs=0.02)

    def test_property_appreciates_at_3pct(self):
        from app.calculators.tax_config import PROPERTY_APPRECIATION_RATE

        result = project_keep(**KEEP_BASE)
        for entry in result:
            expected_value = round(500_000.0 * (1 + PROPERTY_APPRECIATION_RATE) ** entry["year"], 2)
            assert entry["property_value"] == pytest.approx(expected_value, rel=1e-4)

    def test_no_mortgage_balance_stays_zero(self):
        result = project_keep(**KEEP_BASE)
        assert all(e["mortgage_balance"] == 0.0 for e in result)

    def test_cumulative_cf_accumulates(self):
        result = project_keep(**KEEP_BASE)
        running = 0.0
        for entry in result:
            running += entry["annual_cash_flow"]
            assert entry["cumulative_cash_flow"] == pytest.approx(running, abs=0.02)

    def test_total_is_equity_plus_cumulative_cf(self):
        result = project_keep(**KEEP_BASE)
        for entry in result:
            assert entry["total"] == pytest.approx(entry["equity"] + entry["cumulative_cash_flow"], abs=0.02)

    def test_with_mortgage_balance_decreases(self):
        params = {
            **KEEP_BASE,
            "has_mortgage": True,
            "mortgage_balance": 300_000.0,
            "mortgage_annual_rate": 0.05,
            "mortgage_months_remaining": 240,
        }
        result = project_keep(**params)
        balances = [e["mortgage_balance"] for e in result]
        # Mortgage balance should be strictly decreasing each year
        assert balances == sorted(balances, reverse=True)

    def test_with_mortgage_equity_grows(self):
        params = {
            **KEEP_BASE,
            "has_mortgage": True,
            "mortgage_balance": 200_000.0,
            "mortgage_annual_rate": 0.04,
            "mortgage_months_remaining": 300,
        }
        result = project_keep(**params)
        equities = [e["equity"] for e in result]
        # Equity should grow year-over-year (appreciation > repayment is typical)
        assert equities[-1] > equities[0]

    def test_zero_rent_negative_or_zero_cash_flow(self):
        # No rent + expenses → cash flow ≤ 0
        params = {**KEEP_BASE, "monthly_gross_rent": 0.0}
        result = project_keep(**params)
        assert all(e["annual_cash_flow"] <= 0.0 for e in result)
