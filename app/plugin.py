"""Embeddable Fort Knox track: operator runs trains; we meter the toll."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app import config, store
from app.toll import charge_toll


class Track:
    """Self-hosted plugin. Call `report` when a train completes a transaction."""

    def __init__(
        self,
        operator_id: str,
        *,
        settlement_mode: str | None = None,
    ) -> None:
        if not operator_id:
            raise ValueError("operator_id is required")
        self.operator_id = operator_id
        self.settlement_mode = settlement_mode or config.DEFAULT_SETTLEMENT_MODE

    def report(
        self,
        operator_tx_id: str,
        *,
        settlement_mode: str | None = None,
    ) -> dict:
        """Passive toll: one $0.002 receipt per operator_tx_id. We don't run the train."""
        if not operator_tx_id:
            raise ValueError("operator_tx_id is required")

        existing = store.get_by_partner_tx(self.operator_id, operator_tx_id)
        if existing:
            return existing

        tx_id = f"tx_{uuid4().hex[:16]}"
        route_id = f"{config.TRACK_ROUTE_PREFIX}-{uuid4().hex[:12]}"
        mode = settlement_mode or self.settlement_mode
        receipt = charge_toll(
            transaction_id=tx_id,
            partner_id=self.operator_id,
            settlement_mode=mode,
        )
        record = {
            "transaction_id": tx_id,
            "status": "completed",
            "operator_id": self.operator_id,
            "partner_id": self.operator_id,
            "operator_tx_id": operator_tx_id,
            "partner_tx_id": operator_tx_id,
            "track_route_id": route_id,
            "toll_usd": config.TOLL_USD,
            "toll_crypto": {
                "amount": receipt["toll_crypto_amount"],
                "asset": receipt["toll_crypto_asset"],
                "settlement_mode": receipt["settlement_mode"],
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "receipt_id": receipt["receipt_id"],
            "treasury_address": receipt.get("treasury_address", ""),
            "treasury_chain": receipt.get("treasury_chain", ""),
            "live_send": receipt.get("live_send", False),
            "live_send_status": receipt.get("live_send_status"),
            "live_intent": receipt.get("live_intent"),
        }
        store.save_transaction(tx_id, record)
        return record
