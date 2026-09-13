"""USDC-on-Base live settlement — fail-closed, no private keys.

Circle native USDC on Base:
https://developers.circle.com/stablecoins/usdc-contract-addresses
"""

from __future__ import annotations

import os

# Circle native USDC (Base mainnet). 6 decimals. Chain id 8453.
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
BASE_CHAIN_ID = 8453
USDC_DECIMALS = 6
TRANSFER_SELECTOR = "a9059cbb"


class LiveSendBlocked(RuntimeError):
    """LIVE_SEND is on but we will not broadcast (no key, no signer)."""


def usdc_units(usd: float) -> int:
    return int(round(usd * (10**USDC_DECIMALS)))


def evm_word(hex_or_int: str | int) -> str:
    if isinstance(hex_or_int, int):
        return f"{hex_or_int:064x}"
    raw = hex_or_int.lower().removeprefix("0x")
    return raw.zfill(64)


def build_usdc_base_intent(*, to: str, usd: float = 0.002) -> dict:
    """Unsigned ERC-20 transfer of `usd` USDC on Base. Does not broadcast."""
    if not to or not to.startswith("0x") or len(to) != 42:
        raise ValueError("live settle needs a 20-byte EVM public treasury address")
    units = usdc_units(usd)
    if units <= 0:
        raise ValueError("toll units must be > 0")
    data = "0x" + TRANSFER_SELECTOR + evm_word(to) + evm_word(units)
    return {
        "chain": "base",
        "chain_id": BASE_CHAIN_ID,
        "token": USDC_BASE,
        "token_decimals": USDC_DECIMALS,
        "to": to,
        "amount_usd": usd,
        "amount_units": units,
        "data": data,
        "broadcast": False,
    }


def broadcast_usdc_base(intent: dict) -> str:
    """Refuse to send unless an external signer URL exists. Never load a private key."""
    if os.environ.get("FORT_KNOX_PRIVATE_KEY") or os.environ.get("PRIVATE_KEY"):
        raise LiveSendBlocked(
            "A private-key env var is set; refusing to use it. "
            "Remove it. Live send only via an external signer you control."
        )
    signer = os.environ.get("FORT_KNOX_SIGNER_URL", "").strip()
    if not signer:
        raise LiveSendBlocked(
            "LIVE_SEND is on but no FORT_KNOX_SIGNER_URL is configured. "
            "Failing closed — no on-chain send, no private key loaded."
        )
    raise LiveSendBlocked(
        "External signer hook is not enabled in this build. Failing closed."
    )


def live_settle_or_block(*, treasury_address: str, usd: float = 0.002) -> dict:
    intent = build_usdc_base_intent(to=treasury_address, usd=usd)
    broadcast_usdc_base(intent)
    return intent
