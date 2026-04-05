"""
Tests for app/calculators/tax.py

All expected values are computed by hand against the 2026 brackets:
  Federal: 14% ≤ $58,523 / 20.5% ≤ $117,045 / 26% ≤ $181,440 / 29% ≤ $258,482 / 33% above
  Quebec:  14% ≤ $54,295 / 19% ≤ $108,570 / 24% ≤ $132,000 / 25.75% above
  Federal BPA: $16,129   Quebec BPA: $17,183
  Quebec Abatement: 16.5%
"""

import pytest
from app.calculators.tax import (
    bracket_tax,
    federal_tax,
    provincial_tax,
    combined_tax,
    marginal_tax_on_income,
    compute_oas_clawback,
)
from app.calculators.tax_config import (
    FEDERAL_BRACKETS_2026,
    QUEBEC_BRACKETS_2026,
    FEDERAL_BPA_2026,
    QUEBEC_BPA_2026,
    OAS_CLAWBACK_THRESHOLD_2026,
    OAS_CLAWBACK_RATE,
    OAS_MAX_ANNUAL_65_74,
    OAS_MAX_ANNUAL_75_PLUS,
)


# ---------------------------------------------------------------------------
# bracket_tax
# ---------------------------------------------------------------------------


class TestBracketTax:
    def test_zero_income(self):
        assert bracket_tax(0.0, FEDERAL_BRACKETS_2026) == 0.0

    def test_negative_income(self):
        assert bracket_tax(-1_000.0, FEDERAL_BRACKETS_2026) == 0.0

    def test_first_bracket_only(self):
        # $30,000 entirely in the 14% federal bracket
        assert bracket_tax(30_000.0, FEDERAL_BRACKETS_2026) == pytest.approx(30_000 * 0.14, rel=1e-6)

    def test_spans_two_federal_brackets(self):
        # $80,000: first $58,523 @ 14%, next $21,477 @ 20.5%
        expected = 58_523 * 0.14 + (80_000 - 58_523) * 0.205
        assert bracket_tax(80_000.0, FEDERAL_BRACKETS_2026) == pytest.approx(expected, rel=1e-6)

    def test_all_federal_brackets(self):
        # $300,000 spans all five federal brackets
        income = 300_000.0
        expected = 58_523 * 0.14 + (117_045 - 58_523) * 0.205 + (181_440 - 117_045) * 0.26 + (258_482 - 181_440) * 0.29 + (300_000 - 258_482) * 0.33
        assert bracket_tax(income, FEDERAL_BRACKETS_2026) == pytest.approx(expected, rel=1e-6)

    def test_exact_bracket_boundary(self):
        # Income exactly at the first federal bracket ceiling
        assert bracket_tax(58_523.0, FEDERAL_BRACKETS_2026) == pytest.approx(58_523 * 0.14, rel=1e-6)

    def test_quebec_first_bracket(self):
        assert bracket_tax(30_000.0, QUEBEC_BRACKETS_2026) == pytest.approx(30_000 * 0.14, rel=1e-6)

    def test_quebec_top_bracket(self):
        # $140,000: spans all four Quebec brackets
        income = 140_000.0
        expected = 54_295 * 0.14 + (108_570 - 54_295) * 0.19 + (132_000 - 108_570) * 0.24 + (140_000 - 132_000) * 0.2575
        assert bracket_tax(income, QUEBEC_BRACKETS_2026) == pytest.approx(expected, rel=1e-6)


# ---------------------------------------------------------------------------
# federal_tax  (after BPA credit + 16.5% Quebec Abatement)
# ---------------------------------------------------------------------------


class TestFederalTax:
    def test_zero_income(self):
        assert federal_tax(0.0) == 0.0

    def test_below_bpa(self):
        # Below BPA → no federal tax
        assert federal_tax(FEDERAL_BPA_2026 - 1) == 0.0

    def test_at_bpa(self):
        # Exactly at BPA → after credit, no federal tax
        assert federal_tax(FEDERAL_BPA_2026) == 0.0

    def test_moderate_income(self):
        # $50,000: hand-computed
        # gross  = 50_000 * 0.14 = 7_000
        # bpa_credit = 16_129 * 0.14 = 2_258.06
        # net_before_abatement = 7_000 - 2_258.06 = 4_741.94
        # after_abatement = 4_741.94 * (1 - 0.165) = 3_959.52 (approx)
        gross = 50_000 * 0.14
        bpa_credit = FEDERAL_BPA_2026 * 0.14
        net = (gross - bpa_credit) * (1 - 0.165)
        assert federal_tax(50_000.0) == pytest.approx(net, rel=1e-6)

    def test_high_income(self):
        # $200,000 — crosses four brackets
        gross = 58_523 * 0.14 + (117_045 - 58_523) * 0.205 + (181_440 - 117_045) * 0.26 + (200_000 - 181_440) * 0.29
        bpa_credit = FEDERAL_BPA_2026 * 0.14
        expected = max(0.0, gross - bpa_credit) * (1 - 0.165)
        assert federal_tax(200_000.0) == pytest.approx(expected, rel=1e-6)

    def test_non_negative(self):
        for income in [0, 1_000, 50_000, 500_000]:
            assert federal_tax(float(income)) >= 0.0


# ---------------------------------------------------------------------------
# provincial_tax
# ---------------------------------------------------------------------------


class TestProvincialTax:
    def test_zero_income(self):
        assert provincial_tax(0.0) == 0.0

    def test_below_bpa(self):
        assert provincial_tax(QUEBEC_BPA_2026 - 1) == 0.0

    def test_moderate_income(self):
        # $60,000 — spans two Quebec brackets
        gross = 54_295 * 0.14 + (60_000 - 54_295) * 0.19
        bpa_credit = QUEBEC_BPA_2026 * 0.14
        expected = max(0.0, gross - bpa_credit)
        assert provincial_tax(60_000.0) == pytest.approx(expected, rel=1e-6)

    def test_non_negative(self):
        for income in [0, 1_000, 60_000, 500_000]:
            assert provincial_tax(float(income)) >= 0.0


# ---------------------------------------------------------------------------
# combined_tax
# ---------------------------------------------------------------------------


class TestCombinedTax:
    def test_combined_equals_sum_of_parts(self):
        for income in [40_000.0, 100_000.0, 250_000.0]:
            assert combined_tax(income) == pytest.approx(federal_tax(income) + provincial_tax(income), rel=1e-9)

    def test_zero(self):
        assert combined_tax(0.0) == 0.0

    def test_monotone(self):
        # Higher income must produce equal or higher combined tax
        values = [combined_tax(float(i)) for i in [30_000, 60_000, 120_000, 250_000]]
        assert values == sorted(values)


# ---------------------------------------------------------------------------
# marginal_tax_on_income
# ---------------------------------------------------------------------------


class TestMarginalTaxOnIncome:
    def test_zero_additional(self):
        result = marginal_tax_on_income(50_000.0, 0.0)
        assert result["federal"] == pytest.approx(0.0, abs=1e-9)
        assert result["provincial"] == pytest.approx(0.0, abs=1e-9)
        assert result["total"] == pytest.approx(0.0, abs=1e-9)

    def test_keys_present(self):
        result = marginal_tax_on_income(50_000.0, 20_000.0)
        assert set(result.keys()) == {"federal", "provincial", "total"}

    def test_total_equals_federal_plus_provincial(self):
        result = marginal_tax_on_income(40_000.0, 30_000.0)
        assert result["total"] == pytest.approx(result["federal"] + result["provincial"], rel=1e-9)

    def test_stacking_increases_tax(self):
        # Adding income on top of a base should increase tax
        base = marginal_tax_on_income(0.0, 50_000.0)["total"]
        stacked = marginal_tax_on_income(50_000.0, 50_000.0)["total"]
        assert stacked >= base

    def test_marginal_rate_in_top_bracket(self):
        # At $300k base + $50k additional: both in top brackets
        result = marginal_tax_on_income(300_000.0, 50_000.0)
        # Federal top: 33% * (1 - 0.165) = 27.555%
        # Quebec top:  25.75%
        # Combined marginal ≈ 53.3%
        effective_rate = result["total"] / 50_000.0
        assert 0.50 < effective_rate < 0.60

    def test_non_negative_all_outputs(self):
        result = marginal_tax_on_income(80_000.0, 15_000.0)
        assert result["federal"] >= 0.0
        assert result["provincial"] >= 0.0
        assert result["total"] >= 0.0


# ---------------------------------------------------------------------------
# compute_oas_clawback
# ---------------------------------------------------------------------------


class TestComputeOasClawback:
    def test_under_65_no_clawback(self):
        # Age 64 — OAS not yet received, zero clawback regardless of income
        assert compute_oas_clawback(0.0, 500_000.0, age=64) == pytest.approx(0.0)

    def test_age_65_no_clawback_below_threshold(self):
        # Total income below threshold → no clawback
        assert compute_oas_clawback(0.0, OAS_CLAWBACK_THRESHOLD_2026 - 1, age=65) == pytest.approx(0.0)

    def test_age_65_incremental_clawback(self):
        # Base $80k, additional $50k → total $130k
        # Incremental clawback = 15% of ($130k - threshold) - 15% of max(0, $80k - threshold)
        # Assuming threshold > $80k: clawback_on_base = 0
        # clawback_on_total = min(OAS_MAX_65_74, (130k - threshold) * 0.15)
        base = 80_000.0
        additional = 50_000.0
        total = base + additional
        expected_on_total = min(OAS_MAX_ANNUAL_65_74, max(0.0, total - OAS_CLAWBACK_THRESHOLD_2026) * OAS_CLAWBACK_RATE)
        expected_on_base = min(OAS_MAX_ANNUAL_65_74, max(0.0, base - OAS_CLAWBACK_THRESHOLD_2026) * OAS_CLAWBACK_RATE)
        expected = max(0.0, expected_on_total - expected_on_base)
        assert compute_oas_clawback(base, additional, age=65) == pytest.approx(expected, rel=1e-6)

    def test_clawback_capped_at_max_benefit_65_74(self):
        # Very high income — clawback should not exceed maximum OAS benefit
        result = compute_oas_clawback(0.0, 2_000_000.0, age=70)
        assert result <= OAS_MAX_ANNUAL_65_74 + 1e-6

    def test_clawback_capped_at_max_benefit_75_plus(self):
        # 75+ receives a higher supplement
        result = compute_oas_clawback(0.0, 2_000_000.0, age=75)
        assert result <= OAS_MAX_ANNUAL_75_PLUS + 1e-6

    def test_age_75_higher_cap_than_65(self):
        # Same income, age 75+ should have same or higher clawback cap
        clawback_65 = compute_oas_clawback(0.0, 2_000_000.0, age=65)
        clawback_75 = compute_oas_clawback(0.0, 2_000_000.0, age=75)
        assert clawback_75 >= clawback_65

    def test_incremental_only_above_base(self):
        # Base income already above threshold — only the portion above baseline
        # clawback should be captured, not re-taxing the base portion
        base = OAS_CLAWBACK_THRESHOLD_2026 + 10_000.0
        additional = 5_000.0
        result = compute_oas_clawback(base, additional, age=67)
        # Incremental: 15% of $5,000 additional = $750 (below OAS max)
        assert result == pytest.approx(additional * OAS_CLAWBACK_RATE, rel=1e-6)

    def test_zero_additional_income_no_clawback(self):
        assert compute_oas_clawback(50_000.0, 0.0, age=68) == pytest.approx(0.0)

    def test_non_negative(self):
        assert compute_oas_clawback(0.0, 100_000.0, age=66) >= 0.0
