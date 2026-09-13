"""Toll collector: mock ledger + optional crypto stubs. No fake balances."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from app import config
from app import store


def crypto_amount_for_toll(asset: str, toll_usd: float = config.TOLL_USD) -> float:
    price = config.MOCK_USD_PRICES.get(asset)
    if price is None or price <= 0:
        raise ValueError(f"No mock price for asset: {asset}")
    # Round for readability; not for production settlement.
    return round(toll_usd / price, 12)


def charge_toll(
    *,
    transaction_id: str,
    partner_id: str,
    settlement_mode: str | None = None,
) -> dict:
    """Record a $0.002 toll. partner_id is the operator_id (alias kept for callers).

    Default path is the mock ledger. When LIVE_SEND is env-enabled, a
    USDC-on-Base intent is attached (still no broadcast without an
    explicit operator-pay signer config).
    """
    mode = settlement_mode or config.DEFAULT_SETTLEMENT_MODE
    if mode not in config.SETTLEMENT_ASSET:
        raise ValueError(f"Unknown settlement_mode: {mode}")

    asset = config.SETTLEMENT_ASSET[mode]
    amount = crypto_amount_for_toll(asset)
    operator_id = partner_id

    receipt = {
        "receipt_id": f"rcpt_{uuid4().hex[:16]}",
        "transaction_id": transaction_id,
        "operator_id": operator_id,
        "partner_id": operator_id,
        "toll_usd": config.TOLL_USD,
        "toll_crypto_amount": amount,
        "toll_crypto_asset": asset,
        "settlement_mode": mode,
        "charged_at": datetime.now(timezone.utc).isoformat(),
        "status": "recorded",
        "note": "Mock/stub settlement only — no real balance or on-chain transfer.",
        **config.treasury_public(),
    }

    if config.LIVE_SEND:
        from app.live_send import attach_usdc_base_intent

        attach_usdc_base_intent(receipt)

    store.save_receipt(receipt["receipt_id"], receipt)
    return receipt
