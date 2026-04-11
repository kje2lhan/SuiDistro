"""Core distribution logic for SuiDistro."""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Iterable, Optional, Protocol, runtime_checkable

from .models import DistributionResult, DistributionSummary, Recipient

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Thin protocol for the Sui RPC client so that the distributor can be         #
# tested without a live network connection.                                   #
# --------------------------------------------------------------------------- #
@runtime_checkable
class SuiClientProtocol(Protocol):
    """Minimal interface expected from a Sui RPC client."""

    def transfer_sui(
        self,
        signer: str,
        recipient: str,
        amount: int,
        gas_budget: int,
    ) -> str:
        """Submit a SUI transfer and return the transaction digest."""
        ...  # pragma: no cover


# --------------------------------------------------------------------------- #
# Optional live-client helper (requires pysui to be installed).               #
# --------------------------------------------------------------------------- #
def _build_pysui_client(
    rpc_url: str, signer_address: str, keystore_path: Optional[str] = None
) -> "SuiClientProtocol":  # noqa: F821
    """Construct a pysui-backed client.

    Args:
        rpc_url: Sui full-node RPC endpoint
                 (e.g. ``"https://fullnode.mainnet.sui.io:443"``).
        signer_address: The 0x-prefixed address of the sender.
        keystore_path: Path to the Sui CLI keystore file.  When *None* the
                       pysui default location (``~/.sui/sui_config/sui.keystore``)
                       is used.

    Returns:
        A :class:`SuiClientProtocol`-compatible pysui client wrapper.

    Raises:
        ImportError: If pysui is not installed.
    """
    try:
        from pysui import SuiConfig, SyncClient  # type: ignore[import]
        from pysui.sui.sui_txn import SyncTransaction  # type: ignore[import]
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "pysui is required for live Sui network access. "
            "Install it with:  pip install pysui"
        ) from exc

    class _PySuiAdapter:
        def __init__(self) -> None:
            cfg_kwargs: dict = {"rpc_url": rpc_url}
            if keystore_path:
                cfg_kwargs["keystore_path"] = keystore_path
            self._cfg = SuiConfig.user_config(**cfg_kwargs)
            self._client = SyncClient(self._cfg)
            self._signer = signer_address

        def transfer_sui(
            self,
            signer: str,
            recipient: str,
            amount: int,
            gas_budget: int,
        ) -> str:
            txn = SyncTransaction(client=self._client, initial_sender=signer)
            txn.transfer_sui(
                recipient=txn.pure.address(recipient),
                from_coin=txn.gas,
                amount=txn.pure.u64(amount),
            )
            result = txn.execute(gas_budget=gas_budget)
            if result.is_ok():
                return result.result_data.digest
            raise RuntimeError(result.result_string)

    return _PySuiAdapter()


# --------------------------------------------------------------------------- #
# Public distributor                                                          #
# --------------------------------------------------------------------------- #
class SuiDistributor:
    """Distribute SUI tokens to a list of recipients.

    Parameters:
        client: A :class:`SuiClientProtocol`-compatible RPC client.
        signer: The 0x-prefixed address of the funding wallet.
        gas_budget: Gas budget in MIST for each transaction
                    (default: 5_000_000 MIST = 0.005 SUI).
        dry_run: When *True*, log what would be sent but don't submit any
                 transactions.

    Example::

        from src import SuiDistributor, Recipient

        distributor = SuiDistributor(client=my_client, signer="0x...")
        recipients = [Recipient.from_sui("0x...", 10.0, label="Alice")]
        summary = distributor.distribute(recipients)
        print(summary.total_sui_sent)
    """

    DEFAULT_GAS_BUDGET: int = 5_000_000

    def __init__(
        self,
        client: SuiClientProtocol,
        signer: str,
        gas_budget: int = DEFAULT_GAS_BUDGET,
        dry_run: bool = False,
    ) -> None:
        self._client = client
        self._signer = signer
        self._gas_budget = gas_budget
        self._dry_run = dry_run

    # ------------------------------------------------------------------ #
    # Factory methods                                                     #
    # ------------------------------------------------------------------ #
    @classmethod
    def from_rpc(
        cls,
        rpc_url: str,
        signer: str,
        keystore_path: Optional[str] = None,
        gas_budget: int = DEFAULT_GAS_BUDGET,
        dry_run: bool = False,
    ) -> "SuiDistributor":
        """Create a distributor that talks directly to a Sui node.

        Args:
            rpc_url: Full-node RPC URL.
            signer: Sender wallet address (must exist in keystore).
            keystore_path: Path to ``sui.keystore``; uses pysui default when
                           *None*.
            gas_budget: Per-transaction gas budget in MIST.
            dry_run: Simulate without submitting transactions.

        Returns:
            A ready-to-use :class:`SuiDistributor`.
        """
        client = _build_pysui_client(rpc_url, signer, keystore_path)
        return cls(client=client, signer=signer, gas_budget=gas_budget, dry_run=dry_run)

    # ------------------------------------------------------------------ #
    # CSV / JSON loaders                                                  #
    # ------------------------------------------------------------------ #
    @staticmethod
    def load_recipients_csv(path: str | Path) -> list[Recipient]:
        """Load recipients from a CSV file.

        Expected columns (order-insensitive, header row required):
        ``address``, ``amount_sui``, ``label`` (optional).

        Args:
            path: Path to the CSV file.

        Returns:
            A list of validated :class:`Recipient` objects.

        Raises:
            ValueError: If a row is malformed or a recipient fails validation.
            FileNotFoundError: If *path* does not exist.
        """
        recipients: list[Recipient] = []
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for i, row in enumerate(reader, start=2):  # row 1 is the header
                try:
                    address = row["address"].strip()
                    amount_sui = float(row["amount_sui"].strip())
                    label = row.get("label", "").strip()
                    r = Recipient.from_sui(address, amount_sui, label)
                    r.validate()
                    recipients.append(r)
                except (KeyError, ValueError) as exc:
                    raise ValueError(f"CSV row {i} is invalid: {exc}") from exc
        return recipients

    @staticmethod
    def load_recipients_json(path: str | Path) -> list[Recipient]:
        """Load recipients from a JSON file.

        Expected format – a list of objects::

            [
              {"address": "0x...", "amount_sui": 10.0, "label": "Alice"},
              ...
            ]

        Args:
            path: Path to the JSON file.

        Returns:
            A list of validated :class:`Recipient` objects.

        Raises:
            ValueError: If a record is malformed or fails validation.
            FileNotFoundError: If *path* does not exist.
        """
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, list):
            raise ValueError("JSON file must contain a top-level list.")
        recipients: list[Recipient] = []
        for i, record in enumerate(data):
            try:
                address = record["address"].strip()
                amount_sui = float(record["amount_sui"])
                label = record.get("label", "")
                r = Recipient.from_sui(address, amount_sui, label)
                r.validate()
                recipients.append(r)
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"JSON record {i} is invalid: {exc}") from exc
        return recipients

    # ------------------------------------------------------------------ #
    # Core distribution                                                   #
    # ------------------------------------------------------------------ #
    def distribute(
        self, recipients: Iterable[Recipient]
    ) -> DistributionSummary:
        """Send SUI to each recipient and return a summary.

        Each transfer is attempted independently; failures are captured in the
        returned :class:`DistributionSummary` rather than aborting the run.

        Args:
            recipients: Iterable of :class:`Recipient` objects to fund.

        Returns:
            A :class:`DistributionSummary` with the outcome of every transfer.
        """
        summary = DistributionSummary()
        for recipient in recipients:
            result = self._transfer_one(recipient)
            summary.results.append(result)
            if result.success:
                logger.info(
                    "Sent %.9f SUI to %s  digest=%s",
                    recipient.amount_sui,
                    recipient.address,
                    result.digest,
                )
            else:
                logger.error(
                    "Failed to send %.9f SUI to %s: %s",
                    recipient.amount_sui,
                    recipient.address,
                    result.error,
                )
        return summary

    # ------------------------------------------------------------------ #
    # Internal helpers                                                    #
    # ------------------------------------------------------------------ #
    def _transfer_one(self, recipient: Recipient) -> DistributionResult:
        """Attempt a single transfer and return its result.

        Args:
            recipient: The recipient to fund.

        Returns:
            A :class:`DistributionResult` describing the outcome.
        """
        try:
            recipient.validate()
        except ValueError as exc:
            return DistributionResult(
                recipient=recipient, success=False, error=str(exc)
            )

        if self._dry_run:
            logger.info(
                "[DRY-RUN] Would send %.9f SUI to %s",
                recipient.amount_sui,
                recipient.address,
            )
            return DistributionResult(
                recipient=recipient, success=True, digest="dry-run"
            )

        try:
            digest = self._client.transfer_sui(
                signer=self._signer,
                recipient=recipient.address,
                amount=recipient.amount_mist,
                gas_budget=self._gas_budget,
            )
            return DistributionResult(recipient=recipient, success=True, digest=digest)
        except Exception as exc:  # noqa: BLE001
            return DistributionResult(
                recipient=recipient, success=False, error=str(exc)
            )
