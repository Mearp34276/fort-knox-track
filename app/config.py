"""Demo configuration. Public treasury address only — never a private key."""

from __future__ import annotations

import os
import re
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # optional; operators may export env instead
    load_dotenv = None  # type: ignore[assignment]

if load_dotenv is not None:
    _env_path = Path(__file__).resolve().parent.parent / ".env"
    if _env_path.is_file():
        load_dotenv(_env_path, override=False)

TOLL_USD = 0.002
DEFAULT_SETTLEMENT_MODE = "mock_ledger"  # mock_ledger | sol_stub | eth_stub | usdc_stub

# Stub USD prices for mock crypto conversion only (demo rates, not live feeds).
MOCK_USD_PRICES = {
    "MOCK": 1.0,  # 1 MOCK unit = $1 for simple arithmetic demos
    "SOL": 150.0,
    "ETH": 3000.0,
    "USDC": 1.0,
}

SETTLEMENT_ASSET = {
    "mock_ledger": "MOCK",
    "sol_stub": "SOL",
    "eth_stub": "ETH",
    "usdc_stub": "USDC",
}

# Legacy fee estimate stub: flat + % of amount (clearly demo/estimated).
LEGACY_FLAT_USD = 0.25
LEGACY_BPS = 15  # 0.15% of principal

# Track "rail" fee in this demo is $0 (toll is separate); operators may negotiate later.
TRACK_RAIL_FEE_USD = 0.0

TRACK_ROUTE_PREFIX = "fk-route"

_HEX64 = re.compile(r"^(?:0x)?[0-9a-fA-F]{64}$")
_TRUE = frozenset({"1", "true", "yes", "on"})
_FORBIDDEN_KEY_ENVS = (
    "FORT_KNOX_PRIVATE_KEY",
    "FORT_KNOX_SECRET_KEY",
    "FORT_KNOX_MNEMONIC",
)
_ALLOWED_SIGNER_MODES = frozenset({"", "operator_pay"})


def public_address_only(value: str) -> str:
    """Accept a public address or empty. Reject obvious private-key material."""
    v = (value or "").strip()
    if not v:
        return ""
    if _HEX64.match(v) or (v.startswith("[") and v.endswith("]")):
        raise ValueError("TREASURY_ADDRESS must be a public address, never a private key")
    return v


def parse_live_send(environ: dict[str, str] | None = None) -> bool:
    """LIVE_SEND / FORT_KNOX_LIVE_SEND default false. Env-only opt-in."""
    env = environ if environ is not None else os.environ
    for name in ("FORT_KNOX_LIVE_SEND", "LIVE_SEND"):
        raw = str(env.get(name, "")).strip().lower()
        if raw in _TRUE:
            return True
    return False


def parse_signer_mode(value: str | None = None) -> str:
    """Explicit operator-pay flow only. Never a private key."""
    v = (os.environ.get("FORT_KNOX_SIGNER_MODE", "") if value is None else value)
    v = (v or "").strip().lower()
    if _HEX64.match(v) or "private" in v or "secret" in v or "mnemonic" in v or "seed" in v:
        raise ValueError(
            "FORT_KNOX_SIGNER_MODE must be 'operator_pay' (or empty), never a private key"
        )
    if v not in _ALLOWED_SIGNER_MODES:
        raise ValueError("Unknown FORT_KNOX_SIGNER_MODE (supported: operator_pay)")
    return v


def parse_signer_url(value: str | None = None) -> str:
    """Optional external signer URL. Never a private key."""
    v = (os.environ.get("FORT_KNOX_SIGNER_URL", "") if value is None else value)
    v = (v or "").strip()
    if not v:
        return ""
    if _HEX64.match(v) or v.startswith("["):
        raise ValueError("FORT_KNOX_SIGNER_URL must be an https URL, never a private key")
    if not (v.startswith("https://") or v.startswith("http://")):
        raise ValueError("FORT_KNOX_SIGNER_URL must be an http(s) URL")
    return v


def reject_private_key_env(environ: dict[str, str] | None = None) -> None:
    """This process never accepts a Fort Knox private key / seed."""
    env = environ if environ is not None else os.environ
    for name in _FORBIDDEN_KEY_ENVS:
        if str(env.get(name, "")).strip():
            raise ValueError(
                f"{name} is not supported. Live mode uses an operator pay flow; "
                "never put a private key in this process or repo."
            )


reject_private_key_env()

# Hard-off unless FORT_KNOX_LIVE_SEND or LIVE_SEND is explicitly truthy in the environment.
LIVE_SEND = parse_live_send()
SIGNER_MODE = parse_signer_mode()
SIGNER_URL = parse_signer_url()

# Empty default: mock meter works with no wallet linked.
TREASURY_ADDRESS = public_address_only(os.environ.get("FORT_KNOX_TREASURY_ADDRESS", ""))
# Default rail: USDC on Base. Override with FORT_KNOX_TREASURY_CHAIN if needed.
TREASURY_CHAIN = os.environ.get("FORT_KNOX_TREASURY_CHAIN", "usdc_base").strip() or "usdc_base"


def treasury_public() -> dict:
    return {
        "treasury_address": TREASURY_ADDRESS or "",
        "treasury_chain": TREASURY_CHAIN or "usdc_base",
        "treasury_linked": bool(TREASURY_ADDRESS),
        "live_send": bool(LIVE_SEND),
    }
