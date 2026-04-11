"""Unit tests for src.models."""

import pytest

from src.models import DistributionResult, DistributionSummary, Recipient

# ------------------------------------------------------------------ #
# Helper addresses                                                    #
# ------------------------------------------------------------------ #
VALID_ADDR = "0x" + "a" * 64  # 66-char address


class TestRecipient:
    def test_from_sui_converts_correctly(self):
        r = Recipient.from_sui(VALID_ADDR, 1.5)
        assert r.amount_mist == 1_500_000_000

    def test_from_sui_fractional(self):
        r = Recipient.from_sui(VALID_ADDR, 0.001)
        assert r.amount_mist == 1_000_000

    def test_amount_sui_property(self):
        r = Recipient(address=VALID_ADDR, amount_mist=2_000_000_000)
        assert r.amount_sui == pytest.approx(2.0)

    def test_from_sui_negative_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            Recipient.from_sui(VALID_ADDR, -1.0)

    def test_validate_passes_for_valid_recipient(self):
        r = Recipient.from_sui(VALID_ADDR, 1.0)
        r.validate()  # should not raise

    def test_validate_rejects_missing_0x_prefix(self):
        r = Recipient(address="a" * 66, amount_mist=1_000_000_000)
        with pytest.raises(ValueError, match="0x"):
            r.validate()

    def test_validate_rejects_wrong_length(self):
        r = Recipient(address="0x" + "a" * 10, amount_mist=1_000_000_000)
        with pytest.raises(ValueError, match="66 characters"):
            r.validate()

    def test_validate_rejects_zero_amount(self):
        r = Recipient(address=VALID_ADDR, amount_mist=0)
        with pytest.raises(ValueError, match="positive"):
            r.validate()

    def test_validate_rejects_negative_amount(self):
        r = Recipient(address=VALID_ADDR, amount_mist=-1)
        with pytest.raises(ValueError, match="positive"):
            r.validate()

    def test_label_defaults_to_empty_string(self):
        r = Recipient.from_sui(VALID_ADDR, 1.0)
        assert r.label == ""

    def test_label_stored(self):
        r = Recipient.from_sui(VALID_ADDR, 1.0, label="Alice")
        assert r.label == "Alice"


class TestDistributionSummary:
    def _make_result(self, success: bool, amount_mist: int = 1_000_000_000):
        r = Recipient(address=VALID_ADDR, amount_mist=amount_mist)
        return DistributionResult(recipient=r, success=success, digest="abc" if success else None)

    def test_succeeded_filters_correctly(self):
        summary = DistributionSummary(
            results=[self._make_result(True), self._make_result(False)]
        )
        assert len(summary.succeeded) == 1
        assert summary.succeeded[0].success is True

    def test_failed_filters_correctly(self):
        summary = DistributionSummary(
            results=[self._make_result(True), self._make_result(False)]
        )
        assert len(summary.failed) == 1
        assert summary.failed[0].success is False

    def test_total_sui_sent_counts_only_successes(self):
        summary = DistributionSummary(
            results=[
                self._make_result(True, 1_000_000_000),   # 1 SUI success
                self._make_result(False, 2_000_000_000),  # 2 SUI failure
                self._make_result(True, 500_000_000),     # 0.5 SUI success
            ]
        )
        assert summary.total_sui_sent == pytest.approx(1.5)

    def test_empty_summary(self):
        summary = DistributionSummary()
        assert summary.succeeded == []
        assert summary.failed == []
        assert summary.total_sui_sent == pytest.approx(0.0)
