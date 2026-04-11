"""Unit tests for src.distributor (no live network required)."""

from __future__ import annotations

import json
import csv
import textwrap
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.distributor import SuiDistributor
from src.models import Recipient

# ------------------------------------------------------------------ #
# Helper addresses                                                    #
# ------------------------------------------------------------------ #
ADDR_A = "0x" + "a" * 64
ADDR_B = "0x" + "b" * 64


def make_mock_client(digest: str = "fakedigest123") -> MagicMock:
    """Return a mock that satisfies :class:`SuiClientProtocol`."""
    client = MagicMock()
    client.transfer_sui.return_value = digest
    return client


# ------------------------------------------------------------------ #
# distribute()                                                        #
# ------------------------------------------------------------------ #
class TestDistribute:
    def test_successful_transfer(self):
        client = make_mock_client("digest-ok")
        d = SuiDistributor(client=client, signer=ADDR_A)
        recipients = [Recipient.from_sui(ADDR_B, 1.0)]
        summary = d.distribute(recipients)

        assert len(summary.succeeded) == 1
        assert summary.failed == []
        assert summary.results[0].digest == "digest-ok"
        client.transfer_sui.assert_called_once_with(
            signer=ADDR_A,
            recipient=ADDR_B,
            amount=1_000_000_000,
            gas_budget=SuiDistributor.DEFAULT_GAS_BUDGET,
        )

    def test_multiple_recipients(self):
        client = make_mock_client()
        d = SuiDistributor(client=client, signer=ADDR_A)
        recipients = [
            Recipient.from_sui(ADDR_A, 5.0),
            Recipient.from_sui(ADDR_B, 3.0),
        ]
        summary = d.distribute(recipients)
        assert len(summary.succeeded) == 2
        assert summary.total_sui_sent == pytest.approx(8.0)

    def test_client_exception_recorded_as_failure(self):
        client = MagicMock()
        client.transfer_sui.side_effect = RuntimeError("network timeout")
        d = SuiDistributor(client=client, signer=ADDR_A)
        summary = d.distribute([Recipient.from_sui(ADDR_B, 1.0)])

        assert len(summary.failed) == 1
        assert "network timeout" in summary.failed[0].error

    def test_invalid_recipient_recorded_as_failure(self):
        client = make_mock_client()
        d = SuiDistributor(client=client, signer=ADDR_A)
        bad = Recipient(address="not-an-address", amount_mist=1_000_000_000)
        summary = d.distribute([bad])

        assert len(summary.failed) == 1
        client.transfer_sui.assert_not_called()

    def test_partial_failure(self):
        client = MagicMock()
        # First call succeeds, second raises.
        client.transfer_sui.side_effect = ["digest-1", RuntimeError("oops")]
        d = SuiDistributor(client=client, signer=ADDR_A)
        summary = d.distribute([
            Recipient.from_sui(ADDR_A, 1.0),
            Recipient.from_sui(ADDR_B, 2.0),
        ])
        assert len(summary.succeeded) == 1
        assert len(summary.failed) == 1

    def test_empty_recipients(self):
        client = make_mock_client()
        d = SuiDistributor(client=client, signer=ADDR_A)
        summary = d.distribute([])
        assert summary.results == []
        client.transfer_sui.assert_not_called()

    def test_custom_gas_budget_passed_to_client(self):
        client = make_mock_client()
        d = SuiDistributor(client=client, signer=ADDR_A, gas_budget=10_000_000)
        d.distribute([Recipient.from_sui(ADDR_B, 1.0)])
        _, kwargs = client.transfer_sui.call_args
        assert kwargs["gas_budget"] == 10_000_000


# ------------------------------------------------------------------ #
# dry_run mode                                                        #
# ------------------------------------------------------------------ #
class TestDryRun:
    def test_dry_run_does_not_call_client(self):
        client = make_mock_client()
        d = SuiDistributor(client=client, signer=ADDR_A, dry_run=True)
        summary = d.distribute([Recipient.from_sui(ADDR_B, 1.0)])

        client.transfer_sui.assert_not_called()
        assert len(summary.succeeded) == 1
        assert summary.results[0].digest == "dry-run"

    def test_dry_run_marks_as_success(self):
        client = make_mock_client()
        d = SuiDistributor(client=client, signer=ADDR_A, dry_run=True)
        summary = d.distribute([Recipient.from_sui(ADDR_B, 100.0)])
        assert summary.results[0].success is True


# ------------------------------------------------------------------ #
# load_recipients_csv()                                               #
# ------------------------------------------------------------------ #
class TestLoadCsv:
    def test_loads_valid_csv(self, tmp_path: Path):
        csv_file = tmp_path / "recipients.csv"
        csv_file.write_text(
            "address,amount_sui,label\n"
            f"{ADDR_A},10.0,Alice\n"
            f"{ADDR_B},5.5,Bob\n",
            encoding="utf-8",
        )
        recipients = SuiDistributor.load_recipients_csv(csv_file)
        assert len(recipients) == 2
        assert recipients[0].label == "Alice"
        assert recipients[0].amount_mist == 10_000_000_000
        assert recipients[1].label == "Bob"

    def test_csv_without_label_column(self, tmp_path: Path):
        csv_file = tmp_path / "recipients.csv"
        csv_file.write_text(
            "address,amount_sui\n"
            f"{ADDR_A},1.0\n",
            encoding="utf-8",
        )
        recipients = SuiDistributor.load_recipients_csv(csv_file)
        assert len(recipients) == 1
        assert recipients[0].label == ""

    def test_csv_bad_row_raises_value_error(self, tmp_path: Path):
        csv_file = tmp_path / "recipients.csv"
        csv_file.write_text(
            "address,amount_sui\n"
            "not-an-address,1.0\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="row 2"):
            SuiDistributor.load_recipients_csv(csv_file)

    def test_csv_missing_column_raises(self, tmp_path: Path):
        csv_file = tmp_path / "recipients.csv"
        csv_file.write_text("address\n" + ADDR_A + "\n", encoding="utf-8")
        with pytest.raises((ValueError, KeyError)):
            SuiDistributor.load_recipients_csv(csv_file)

    def test_csv_nonexistent_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            SuiDistributor.load_recipients_csv(tmp_path / "missing.csv")


# ------------------------------------------------------------------ #
# load_recipients_json()                                              #
# ------------------------------------------------------------------ #
class TestLoadJson:
    def test_loads_valid_json(self, tmp_path: Path):
        json_file = tmp_path / "recipients.json"
        json_file.write_text(
            json.dumps([
                {"address": ADDR_A, "amount_sui": 10.0, "label": "Alice"},
                {"address": ADDR_B, "amount_sui": 5.5},
            ]),
            encoding="utf-8",
        )
        recipients = SuiDistributor.load_recipients_json(json_file)
        assert len(recipients) == 2
        assert recipients[0].amount_mist == 10_000_000_000
        assert recipients[1].label == ""

    def test_json_top_level_not_list_raises(self, tmp_path: Path):
        json_file = tmp_path / "recipients.json"
        json_file.write_text(
            json.dumps({"address": ADDR_A, "amount_sui": 1.0}), encoding="utf-8"
        )
        with pytest.raises(ValueError, match="list"):
            SuiDistributor.load_recipients_json(json_file)

    def test_json_bad_record_raises(self, tmp_path: Path):
        json_file = tmp_path / "recipients.json"
        json_file.write_text(
            json.dumps([{"address": "bad-addr", "amount_sui": 1.0}]),
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="record 0"):
            SuiDistributor.load_recipients_json(json_file)

    def test_json_nonexistent_file_raises(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            SuiDistributor.load_recipients_json(tmp_path / "nope_does_not_exist.json")
