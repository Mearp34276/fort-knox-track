"""Fee optimizer stub — estimates only, labeled as demo."""

from __future__ import annotations

from app import config


def estimate_fees(amount: float) -> dict:
    """Compare a crude legacy fee estimate to track rail fee + toll.

    All figures are DEMO ESTIMATES, not quotes or guarantees.
    """
    legacy = round(config.LEGACY_FLAT_USD + (amount * config.LEGACY_BPS / 10_000), 6)
    track_plus_toll = round(config.TRACK_RAIL_FEE_USD + config.TOLL_USD, 6)
    savings = round(legacy - track_plus_toll, 6)

    return {
        "label": "estimated_demo_only",
        "legacy_estimate_fee_usd": legacy,
        "track_fee_usd": config.TRACK_RAIL_FEE_USD,
        "toll_usd": config.TOLL_USD,
        "track_fee_plus_toll_usd": track_plus_toll,
        "estimated_savings_usd": savings,
        "disclaimer": (
            "Estimated/demo comparison only. Legacy figure uses a flat+$bps stub; "
            "not a real operator quote or guarantee of savings."
        ),
    }
