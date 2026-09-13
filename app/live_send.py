"""USDC-on-Base live settlement scaffold.

Hard-off unless LIVE_SEND / FORT_KNOX_LIVE_SEND is explicitly true in the
environment. This module records a transfer *intent* toward
FORT_KNOX_TREASURY_ADDRESS. It never broadcasts a transaction and never
reads a private key.

Live mode needs an explicit signer / operator-pay flow
(FORT_KNOX_SIGNER_MODE=operator_pay and/or FORT_KNOX_SIGNER_URL).
Without that, the stub refuses to treat the toll as sent.
"""

from __future__ import annotations

from app import config
from app.live_settle import build_usdc_base_intent as _build_erc20_intent


class LiveSendRefused(ValueError):
    """LIVE_SEND is on but the operator-pay / signer flow is not configured."""


def signer_configured() -> bool:
    return bool(getattr(config, "SIGNER_MODE", "") or getattr(config, "SIGNER_URL", ""))


def build_usdc_base_intent() -> dict:
    """Public intent fields for a $0.002 USDC transfer on Base. No broadcast."""
    to = config.TREASURY_ADDRESS or ""
    if to:
        intent = _build_erc20_intent(to=to, usd=config.TOLL_USD)
        intent["asset"] = "USDC"
        intent["token_contract"] = intent.get("token")
        intent["decimals"] = intent.get("token_decimals")
        intent["amount_usdc"] = config.TOLL_USD
        intent["amount_base_units"] = intent.get("amount_units")
        return intent
    return {
        "chain": "base",
        "chain_id": 8453,
        "asset": "USDC",
        "token_contract": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        "decimals": 6,
        "to": "",
        "amount_usd": config.TOLL_USD,
        "amount_usdc": config.TOLL_USD,
        "amount_base_units": 2000,
        "broadcast": False,
    }


def attach_usdc_base_intent(receipt: dict) -> dict:
    """Record a USDC-on-Base intent on the receipt. Never broadcasts.

    Call only when config.LIVE_SEND is true. Without an explicit
    signer / operator-pay config, the send is refused (intent is still
    attached so operators can see the destination).
    """
    intent = build_usdc_base_intent()
    receipt["live_send"] = True
    receipt["live_intent"] = intent

    if not config.TREASURY_ADDRESS:
        intent["status"] = "refused_no_treasury"
        receipt["live_send_status"] = "refused_no_treasury"
        receipt["note"] = (
            "LIVE_SEND is on but FORT_KNOX_TREASURY_ADDRESS is empty. "
            "USDC-on-Base intent not broadcast."
        )
        return receipt

    if not signer_configured():
        intent["status"] = "refused_no_signer"
        receipt["live_send_status"] = "refused_no_signer"
        receipt["note"] = (
            "LIVE_SEND is on: USDC-on-Base intent recorded toward treasury. "
            "No broadcast — set FORT_KNOX_SIGNER_MODE=operator_pay "
            "(operator sends USDC from their own wallet) or FORT_KNOX_SIGNER_URL. "
            "Never put a private key in this repo."
        )
        return receipt

    # operator_pay / signer URL: still do not broadcast from this scaffold.
    intent["status"] = "intent_recorded"
    if config.SIGNER_MODE:
        intent["signer_mode"] = config.SIGNER_MODE
    receipt["live_send_status"] = "intent_recorded_no_broadcast"
    receipt["note"] = (
        "LIVE_SEND is on: USDC-on-Base intent recorded. "
        "This scaffold does not broadcast. Operator-pay flow: send "
        f"{config.TOLL_USD} USDC on Base to {config.TREASURY_ADDRESS}."
    )
    return receipt
