"""In-memory store for the MVP (swap for SQLite later if needed)."""

from __future__ import annotations

from threading import Lock
from typing import Any

_lock = Lock()
_transactions: dict[str, dict[str, Any]] = {}
_receipts: dict[str, dict[str, Any]] = {}
_by_partner_tx: dict[tuple[str, str], str] = {}


def save_transaction(tx_id: str, record: dict[str, Any]) -> None:
    with _lock:
        _transactions[tx_id] = record
        partner_tx_id = record.get("partner_tx_id")
        operator_id = record.get("operator_id") or record.get("partner_id")
        if partner_tx_id and operator_id:
            _by_partner_tx[(operator_id, partner_tx_id)] = tx_id


def get_transaction(tx_id: str) -> dict[str, Any] | None:
    with _lock:
        return _transactions.get(tx_id)


def get_by_partner_tx(partner_id: str, partner_tx_id: str) -> dict[str, Any] | None:
    """Lookup by operator_id (historically named partner_id) + partner_tx_id."""
    with _lock:
        tx_id = _by_partner_tx.get((partner_id, partner_tx_id))
        if not tx_id:
            return None
        return _transactions.get(tx_id)


def list_transactions() -> list[dict[str, Any]]:
    with _lock:
        return list(_transactions.values())


def save_receipt(receipt_id: str, record: dict[str, Any]) -> None:
    with _lock:
        _receipts[receipt_id] = record


def get_receipt(receipt_id: str) -> dict[str, Any] | None:
    with _lock:
        return _receipts.get(receipt_id)


def clear_all() -> None:
    """Test helper."""
    with _lock:
        _transactions.clear()
        _receipts.clear()
        _by_partner_tx.clear()
