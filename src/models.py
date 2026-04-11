"""Data models for SuiDistro."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Recipient:
    """A single token-distribution recipient.

    Attributes:
        address: Sui wallet address (0x-prefixed hex string).
        amount_mist: Amount to send expressed in MIST
                     (1 SUI == 1_000_000_000 MIST).
        label: Optional human-readable label for audit logs.
    """

    address: str
    amount_mist: int
    label: str = ""

    # ------------------------------------------------------------------ #
    # SUI amounts can also be supplied in whole tokens for convenience.   #
    # ------------------------------------------------------------------ #
    @classmethod
    def from_sui(cls, address: str, amount_sui: float, label: str = "") -> "Recipient":
        """Create a :class:`Recipient` from a whole-SUI amount.

        Args:
            address: Target Sui wallet address.
            amount_sui: Amount in SUI tokens (fractions allowed).
            label: Optional label.

        Returns:
            A new :class:`Recipient` with ``amount_mist`` set correctly.
        """
        if amount_sui < 0:
            raise ValueError(f"amount_sui must be non-negative, got {amount_sui}")
        return cls(
            address=address,
            amount_mist=int(amount_sui * 1_000_000_000),
            label=label,
        )

    @property
    def amount_sui(self) -> float:
        """Return the amount as a human-readable SUI value."""
        return self.amount_mist / 1_000_000_000

    def validate(self) -> None:
        """Raise :class:`ValueError` if this recipient is invalid.

        Raises:
            ValueError: If the address format is wrong or the amount is zero
                        or negative.
        """
        if not self.address or not self.address.startswith("0x"):
            raise ValueError(
                f"Invalid Sui address '{self.address}': must start with '0x'."
            )
        if len(self.address) != 66:
            raise ValueError(
                f"Invalid Sui address '{self.address}': expected 66 characters "
                f"(0x + 64 hex digits), got {len(self.address)}."
            )
        if self.amount_mist <= 0:
            raise ValueError(
                f"amount_mist must be positive for address '{self.address}', "
                f"got {self.amount_mist}."
            )


@dataclass
class DistributionResult:
    """Outcome of a single transfer attempt.

    Attributes:
        recipient: The intended recipient.
        success: Whether the transfer was accepted.
        digest: Transaction digest returned by the Sui network (if available).
        error: Error message when ``success`` is ``False``.
    """

    recipient: Recipient
    success: bool
    digest: Optional[str] = None
    error: Optional[str] = None

    def __str__(self) -> str:  # pragma: no cover
        if self.success:
            return (
                f"OK  {self.recipient.address}  "
                f"{self.recipient.amount_sui:.9f} SUI  digest={self.digest}"
            )
        return (
            f"ERR {self.recipient.address}  "
            f"{self.recipient.amount_sui:.9f} SUI  error={self.error}"
        )


@dataclass
class DistributionSummary:
    """Aggregate results of a distribution run.

    Attributes:
        results: Individual transfer outcomes.
    """

    results: list[DistributionResult] = field(default_factory=list)

    @property
    def succeeded(self) -> list[DistributionResult]:
        """Return only the successful transfers."""
        return [r for r in self.results if r.success]

    @property
    def failed(self) -> list[DistributionResult]:
        """Return only the failed transfers."""
        return [r for r in self.results if not r.success]

    @property
    def total_sui_sent(self) -> float:
        """Total SUI successfully distributed."""
        return sum(r.recipient.amount_sui for r in self.succeeded)
