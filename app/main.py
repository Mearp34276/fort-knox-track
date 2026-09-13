"""Fort Knox Track API — plugin of prebuilt tracks + toll meter."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, model_validator

from app import config, store
from app.optimizer import estimate_fees
from app.toll import charge_toll

app = FastAPI(
    title="Fort Knox Track",
    description=(
        "General-purpose plugin of prebuilt tracks. "
        "Operators run their own trains; Fort Knox passively collects "
        "a $0.002 USD-equivalent crypto toll per completed transaction. "
        "Owner: M.E.. Not a licensed bank or money-transmitter product."
    ),
    version="0.1.0",
)


class Purpose(str, Enum):
    borrow = "borrow"
    cash_access = "cash_access"
    other = "other"


class SettlementMode(str, Enum):
    mock_ledger = "mock_ledger"
    sol_stub = "sol_stub"
    eth_stub = "eth_stub"
    usdc_stub = "usdc_stub"


class TransactionRequest(BaseModel):
    amount: float = Field(..., gt=0, description="Transaction principal amount")
    currency: str = Field(..., min_length=3, max_length=8, examples=["USD"])
    operator_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=64,
        description="Preferred. Who runs trains on this track.",
    )
    partner_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=64,
        description="Alias for operator_id (backward compatible).",
    )
    partner_tx_id: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
        description=(
            "Operator idempotency key. Same operator_id + partner_tx_id "
            "returns the original tx; no second toll."
        ),
    )
    purpose: Purpose
    settlement_mode: SettlementMode | None = Field(
        default=None,
        description="Optional; defaults to mock_ledger",
    )

    @model_validator(mode="after")
    def resolve_operator_id(self) -> TransactionRequest:
        resolved = self.operator_id or self.partner_id
        if not resolved:
            raise ValueError("operator_id is required (partner_id accepted as alias)")
        self.operator_id = resolved
        self.partner_id = resolved
        return self


class TransactionResponse(BaseModel):
    transaction_id: str
    status: str
    amount: float
    currency: str
    operator_id: str
    partner_id: str
    partner_tx_id: str | None = None
    purpose: str
    track_route_id: str
    toll_usd: float
    toll_crypto: dict
    fee_comparison: dict
    created_at: str
    receipt_id: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "fort-knox-track",
        "toll_usd": config.TOLL_USD,
        **config.treasury_public(),
    }


class TollReportRequest(BaseModel):
    operator_id: str = Field(..., min_length=1, max_length=64)
    operator_tx_id: str = Field(..., min_length=1, max_length=128)
    settlement_mode: SettlementMode | None = None


class TollReportResponse(BaseModel):
    transaction_id: str
    status: str
    operator_id: str
    operator_tx_id: str
    track_route_id: str
    toll_usd: float
    toll_crypto: dict
    receipt_id: str
    created_at: str
    treasury_address: str = ""
    treasury_chain: str = ""
    live_send: bool = False
    live_send_status: str | None = None
    live_intent: dict | None = None


@app.post("/v1/tolls", response_model=TollReportResponse)
def report_toll(body: TollReportRequest):
    """Passive inbox: operator reports a completed train; we meter $0.002."""
    from app.plugin import Track

    try:
        return Track(body.operator_id, settlement_mode=(body.settlement_mode.value if body.settlement_mode else None)).report(
            body.operator_tx_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc



@app.post("/v1/transactions", response_model=TransactionResponse)
def create_transaction(body: TransactionRequest):
    # submit → route on this track → settle $0.002 toll (one call, three ordered stages)
    operator_id = body.operator_id  # normalized; partner_id is the same value
    if body.partner_tx_id:
        existing = store.get_by_partner_tx(operator_id, body.partner_tx_id)
        if existing:
            return existing

    tx_id = f"tx_{uuid4().hex[:16]}"
    route_id = f"{config.TRACK_ROUTE_PREFIX}-{uuid4().hex[:12]}"
    created_at = datetime.now(timezone.utc).isoformat()
    mode = (body.settlement_mode or SettlementMode.mock_ledger).value

    try:
        receipt = charge_toll(
            transaction_id=tx_id,
            partner_id=operator_id,
            settlement_mode=mode,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    fee_comparison = estimate_fees(body.amount)

    record = {
        "transaction_id": tx_id,
        "status": "completed",
        "amount": body.amount,
        "currency": body.currency.upper(),
        "operator_id": operator_id,
        "partner_id": operator_id,
        "partner_tx_id": body.partner_tx_id,
        "purpose": body.purpose.value,
        "track_route_id": route_id,
        "toll_usd": config.TOLL_USD,
        "toll_crypto": {
            "amount": receipt["toll_crypto_amount"],
            "asset": receipt["toll_crypto_asset"],
            "settlement_mode": receipt["settlement_mode"],
        },
        "fee_comparison": fee_comparison,
        "created_at": created_at,
        "receipt_id": receipt["receipt_id"],
        "treasury_address": receipt.get("treasury_address", ""),
        "treasury_chain": receipt.get("treasury_chain", ""),
        "live_send": receipt.get("live_send", False),
    }
    store.save_transaction(tx_id, record)
    return record


@app.get("/v1/transactions/{transaction_id}")
def get_transaction(transaction_id: str):
    record = store.get_transaction(transaction_id)
    if not record:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return record


@app.get("/v1/receipts/{receipt_id}")
def get_receipt(receipt_id: str):
    receipt = store.get_receipt(receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt


@app.get("/v1/transactions")
def list_transactions(limit: int = Query(50, ge=1, le=200)):
    items = store.list_transactions()
    return {"count": len(items[-limit:]), "transactions": items[-limit:]}
