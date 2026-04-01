"""
Tests for app/calculators/capital_gains.py and app/calculators/cca.py
"""

import pytest
from app.calculators.capital_gains import (
    compute_acb,
    compute_capital_gain,
    compute_taxable_capital_gain,
)
from app.calculators.cca import compute_recapture, compute_terminal_loss
from app.calculators.tax_config import CAPITAL_GAINS_INCLUSION


# ---------------------------------------------------------------------------
# compute_acb
# ---------------------------------------------------------------------------


class TestComputeAcb:
    def test_inherited_uses_fmv(self):
        assert compute_acb(inherited=True, fmv_at_death=400_000.0, user_acb=None) == pytest.approx(400_000.0)

    def test_inherited_ignores_user_acb(self):
        # user_acb should be ignored when inherited=True
        assert compute_acb(inherited=True, fmv_at_death=400_000.0, user_acb=200_000.0) == pytest.approx(400_000.0)

    def test_not_inherited_uses_user_acb(self):
        assert compute_acb(inherited=False, fmv_at_death=None, user_acb=250_000.0) == pytest.approx(250_000.0)

    def test_not_inherited_zero_acb(self):
        # Zero ACB is valid (e.g. gift)
        assert compute_acb(inherited=False, fmv_at_death=None, user_acb=0.0) == pytest.approx(0.0)

    def test_inherited_missing_fmv_raises(self):
        with pytest.raises(ValueError, match="FMV at death"):
            compute_acb(inherited=True, fmv_at_death=None, user_acb=None)

    def test_inherited_zero_fmv_raises(self):
        with pytest.raises(ValueError, match="FMV at death"):
            compute_acb(inherited=True, fmv_at_death=0.0, user_acb=None)

    def test_not_inherited_missing_acb_raises(self):
        with pytest.raises(ValueError, match="ACB"):
            compute_acb(inherited=False, fmv_at_death=None, user_acb=None)

    def test_not_inherited_negative_acb_raises(self):
        with pytest.raises(ValueError, match="ACB"):
            compute_acb(inherited=False, fmv_at_death=None, user_acb=-1.0)


# ---------------------------------------------------------------------------
# compute_capital_gain
# ---------------------------------------------------------------------------


class TestComputeCapitalGain:
    def test_simple_gain(self):
        # Sale $600k, ACB $300k, costs $30k → gain $270k
        gain = compute_capital_gain(
            sale_price=600_000.0,
            acb=300_000.0,
            selling_costs=30_000.0,
            cca_claimed=False,
            original_cost=None,
        )
        assert gain == pytest.approx(270_000.0)

    def test_no_gain_when_acb_exceeds_proceeds(self):
        # Net proceeds $400k, ACB $450k → no gain (loss not reportable here)
        gain = compute_capital_gain(
            sale_price=420_000.0,
            acb=450_000.0,
            selling_costs=20_000.0,
            cca_claimed=False,
            original_cost=None,
        )
        assert gain == pytest.approx(0.0)

    def test_cca_claimed_uses_max_acb_original_cost(self):
        # Sale $700k, ACB $200k, original_cost $350k, costs $20k
        # effective_acb = max(200k, 350k) = 350k
        # gain = 700k - 20k - 350k = 330k
        gain = compute_capital_gain(
            sale_price=700_000.0,
            acb=200_000.0,
            selling_costs=20_000.0,
            cca_claimed=True,
            original_cost=350_000.0,
        )
        assert gain == pytest.approx(330_000.0)

    def test_cca_claimed_acb_higher_than_original_cost(self):
        # If ACB > original_cost, effective_acb = ACB
        gain = compute_capital_gain(
            sale_price=500_000.0,
            acb=300_000.0,
            selling_costs=15_000.0,
            cca_claimed=True,
            original_cost=250_000.0,
        )
        # effective_acb = max(300k, 250k) = 300k; gain = 500k - 15k - 300k = 185k
        assert gain == pytest.approx(185_000.0)

    def test_zero_selling_costs(self):
        gain = compute_capital_gain(
            sale_price=500_000.0,
            acb=300_000.0,
            selling_costs=0.0,
            cca_claimed=False,
            original_cost=None,
        )
        assert gain == pytest.approx(200_000.0)

    def test_gain_is_non_negative(self):
        gain = compute_capital_gain(
            sale_price=100_000.0,
            acb=500_000.0,
            selling_costs=10_000.0,
            cca_claimed=False,
            original_cost=None,
        )
        assert gain >= 0.0


# ---------------------------------------------------------------------------
# compute_taxable_capital_gain
# ---------------------------------------------------------------------------


class TestComputeTaxableCapitalGain:
    def test_50_percent_inclusion(self):
        assert compute_taxable_capital_gain(200_000.0) == pytest.approx(200_000.0 * CAPITAL_GAINS_INCLUSION)

    def test_zero_gain(self):
        assert compute_taxable_capital_gain(0.0) == pytest.approx(0.0)

    def test_inclusion_rate_is_half(self):
        # Verify the constant itself is 0.50
        assert CAPITAL_GAINS_INCLUSION == pytest.approx(0.50)


# ---------------------------------------------------------------------------
# compute_recapture
# ---------------------------------------------------------------------------


class TestComputeRecapture:
    def test_typical_recapture(self):
        # Sale $600k, original $500k, UCC $350k
        # proceeds_for_recapture = min(600k, 500k) = 500k
        # recapture = 500k - 350k = 150k
        assert compute_recapture(600_000.0, 500_000.0, 350_000.0) == pytest.approx(150_000.0)

    def test_no_recapture_when_ucc_above_proceeds(self):
        # UCC > min(sale, original) → recapture = 0
        assert compute_recapture(300_000.0, 500_000.0, 400_000.0) == pytest.approx(0.0)

    def test_sale_below_original_cost_caps_proceeds(self):
        # Sale $250k < original $400k → proceeds_for_recapture capped at $250k
        # UCC $200k → recapture = 250k - 200k = 50k
        assert compute_recapture(250_000.0, 400_000.0, 200_000.0) == pytest.approx(50_000.0)

    def test_sale_equals_ucc_no_recapture(self):
        # proceeds_for_recapture = min(400k, 500k) = 400k = UCC → recapture = 0
        assert compute_recapture(400_000.0, 500_000.0, 400_000.0) == pytest.approx(0.0)

    def test_non_negative(self):
        assert compute_recapture(100_000.0, 500_000.0, 300_000.0) >= 0.0


# ---------------------------------------------------------------------------
# compute_terminal_loss
# ---------------------------------------------------------------------------


class TestComputeTerminalLoss:
    def test_typical_terminal_loss(self):
        # Sale $200k, original $400k, UCC $300k
        # proceeds_for_recapture = min(200k, 400k) = 200k
        # terminal_loss = 300k - 200k = 100k
        assert compute_terminal_loss(200_000.0, 400_000.0, 300_000.0) == pytest.approx(100_000.0)

    def test_no_terminal_loss_when_sale_above_ucc(self):
        assert compute_terminal_loss(500_000.0, 600_000.0, 400_000.0) == pytest.approx(0.0)

    def test_recapture_and_terminal_loss_are_mutually_exclusive(self):
        # The same inputs cannot produce both recapture and terminal loss
        sale, original, ucc = 300_000.0, 500_000.0, 350_000.0
        rec = compute_recapture(sale, original, ucc)
        tl = compute_terminal_loss(sale, original, ucc)
        assert not (rec > 0 and tl > 0)

    def test_non_negative(self):
        assert compute_terminal_loss(100_000.0, 500_000.0, 50_000.0) >= 0.0
