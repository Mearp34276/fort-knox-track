"""API tests for Fort Knox Track MVP."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app import store
from app import config


@pytest.fixture(autouse=True)
def _clear_store(monkeypatch):
    store.clear_all()
    # Tests never enable live broadcast; keep the hard-off default.
    monkeypatch.setattr(config, "LIVE_SEND", False)
    monkeypatch.setattr(config, "SIGNER_MODE", "")
    monkeypatch.setattr(config, "SIGNER_URL", "")
    yield
    store.clear_all()


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["toll_usd"] == config.TOLL_USD


def test_create_transaction(client):
    payload = {
        "amount": 50.0,
        "currency": "USD",
        "partner_id": "demo-partner",
        "purpose": "cash_access",
    }
    r = client.post("/v1/transactions", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "completed"
    assert data["toll_usd"] == 0.002
    assert "transaction_id" in data
    assert data["track_route_id"].startswith("fk-route-")
    assert data["toll_crypto"]["asset"] == "MOCK"
    assert data["toll_crypto"]["amount"] == pytest.approx(0.002)
    assert data["fee_comparison"]["label"] == "estimated_demo_only"
    assert "estimated_savings_usd" in data["fee_comparison"]
    assert data["fee_comparison"]["track_fee_plus_toll_usd"] == pytest.approx(0.002)


def test_purpose_borrow(client):
    r = client.post(
        "/v1/transactions",
        json={
            "amount": 100,
            "currency": "usd",
            "partner_id": "bank-a",
            "purpose": "borrow",
        },
    )
    assert r.status_code == 200
    assert r.json()["purpose"] == "borrow"
    assert r.json()["currency"] == "USD"


def test_sol_stub_settlement(client):
    r = client.post(
        "/v1/transactions",
        json={
            "amount": 10,
            "currency": "USD",
            "partner_id": "p1",
            "purpose": "other",
            "settlement_mode": "sol_stub",
        },
    )
    assert r.status_code == 200
    crypto = r.json()["toll_crypto"]
    assert crypto["asset"] == "SOL"
    assert crypto["settlement_mode"] == "sol_stub"
    assert crypto["amount"] == pytest.approx(0.002 / 150.0)


def test_get_transaction_and_receipt(client):
    created = client.post(
        "/v1/transactions",
        json={
            "amount": 25,
            "currency": "USD",
            "partner_id": "p2",
            "purpose": "cash_access",
        },
    ).json()
    tx = client.get(f"/v1/transactions/{created['transaction_id']}")
    assert tx.status_code == 200
    rcpt = client.get(f"/v1/receipts/{created['receipt_id']}")
    assert rcpt.status_code == 200
    assert rcpt.json()["toll_usd"] == 0.002
    assert "note" in rcpt.json()


def test_reject_invalid_amount(client):
    r = client.post(
        "/v1/transactions",
        json={
            "amount": 0,
            "currency": "USD",
            "partner_id": "p",
            "purpose": "other",
        },
    )
    assert r.status_code == 422


def test_reject_bad_purpose(client):
    r = client.post(
        "/v1/transactions",
        json={
            "amount": 1,
            "currency": "USD",
            "partner_id": "p",
            "purpose": "wire_fraud",
        },
    )
    assert r.status_code == 422


def test_partner_tx_id_is_idempotent(client):
    payload = {
        "amount": 40,
        "currency": "USD",
        "partner_id": "bank-a",
        "partner_tx_id": "loan-99",
        "purpose": "borrow",
    }
    first = client.post("/v1/transactions", json=payload).json()
    second = client.post("/v1/transactions", json=payload).json()
    assert first["transaction_id"] == second["transaction_id"]
    assert first["receipt_id"] == second["receipt_id"]
    assert first["toll_usd"] == 0.002
    listed = client.get("/v1/transactions").json()
    assert listed["count"] == 1


def test_passive_toll_inbox(client):
    payload = {"operator_id": "anyone", "operator_tx_id": "job-1"}
    first = client.post("/v1/tolls", json=payload)
    assert first.status_code == 200
    data = first.json()
    assert data["toll_usd"] == 0.002
    assert data["operator_id"] == "anyone"
    assert data["operator_tx_id"] == "job-1"
    second = client.post("/v1/tolls", json=payload).json()
    assert second["transaction_id"] == data["transaction_id"]
    assert second["receipt_id"] == data["receipt_id"]


def test_embeddable_track_report():
    from app.plugin import Track

    track = Track("solo-op")
    a = track.report("train-7")
    b = track.report("train-7")
    assert a["receipt_id"] == b["receipt_id"]
    assert a["toll_usd"] == 0.002
    assert "amount" not in a


def test_treasury_slot_empty_by_default(monkeypatch, client):
    # Public default: empty address even if a local .env leaked into the shell.
    monkeypatch.setattr(config, "TREASURY_ADDRESS", "")
    monkeypatch.setattr(config, "TREASURY_CHAIN", "usdc_base")
    monkeypatch.setattr(config, "LIVE_SEND", False)
    h = client.get("/health").json()
    assert h["treasury_address"] == ""
    assert h["treasury_chain"] == "usdc_base"
    assert h["treasury_linked"] is False
    assert h["live_send"] is False
    r = client.post("/v1/tolls", json={"operator_id": "op", "operator_tx_id": "t-empty"})
    assert r.status_code == 200
    assert r.json()["treasury_address"] == ""
    assert r.json()["treasury_chain"] == "usdc_base"
    assert r.json()["live_send"] is False


def test_treasury_public_address_on_receipt(monkeypatch, client):
    monkeypatch.setattr(config, "TREASURY_ADDRESS", "0x1111111111111111111111111111111111111111")
    monkeypatch.setattr(config, "TREASURY_CHAIN", "usdc_base")
    r = client.post("/v1/tolls", json={"operator_id": "op", "operator_tx_id": "t-linked"})
    assert r.status_code == 200
    assert r.json()["treasury_address"] == "0x1111111111111111111111111111111111111111"
    receipt = client.get(f"/v1/receipts/{r.json()['receipt_id']}").json()
    assert receipt["treasury_address"].startswith("0x")
    assert receipt["live_send"] is False


def test_rejects_private_key_shaped_treasury():
    from app.config import public_address_only

    with pytest.raises(ValueError, match="public address"):
        public_address_only("0x" + "ab" * 32)


def test_live_send_defaults_false():
    from app.config import parse_live_send

    assert parse_live_send({}) is False
    assert parse_live_send({"LIVE_SEND": ""}) is False
    assert parse_live_send({"LIVE_SEND": "false"}) is False
    assert parse_live_send({"FORT_KNOX_LIVE_SEND": "0"}) is False
    assert parse_live_send({"FORT_KNOX_LIVE_SEND": "true"}) is True
    assert parse_live_send({"LIVE_SEND": "1"}) is True
    assert parse_live_send({"LIVE_SEND": "yes"}) is True


def test_live_send_refuses_without_signer(monkeypatch):
    from app.live_send import attach_usdc_base_intent

    monkeypatch.setattr(config, "LIVE_SEND", True)
    monkeypatch.setattr(config, "SIGNER_MODE", "")
    monkeypatch.setattr(config, "TREASURY_ADDRESS", "0x1111111111111111111111111111111111111111")
    receipt = {"note": "mock"}
    attach_usdc_base_intent(receipt)
    assert receipt["live_send"] is True
    assert receipt["live_send_status"] == "refused_no_signer"
    assert receipt["live_intent"]["broadcast"] is False
    assert receipt["live_intent"]["to"] == "0x1111111111111111111111111111111111111111"
    assert receipt["live_intent"]["asset"] == "USDC"
    assert receipt["live_intent"]["chain"] == "base"
    assert receipt["live_intent"]["amount_base_units"] == 2000
    assert "private" not in receipt["note"].lower() or "never put a private key" in receipt["note"].lower()


def test_live_send_operator_pay_records_intent_no_broadcast(monkeypatch):
    from app.live_send import attach_usdc_base_intent
    from app.toll import charge_toll

    monkeypatch.setattr(config, "LIVE_SEND", True)
    monkeypatch.setattr(config, "SIGNER_MODE", "operator_pay")
    monkeypatch.setattr(config, "TREASURY_ADDRESS", "0x2222222222222222222222222222222222222222")
    receipt = charge_toll(transaction_id="tx_live", partner_id="op-live")
    assert receipt["live_send"] is True
    assert receipt["live_send_status"] == "intent_recorded_no_broadcast"
    assert receipt["live_intent"]["broadcast"] is False
    assert receipt["live_intent"]["status"] == "intent_recorded"
    assert receipt["live_intent"]["to"] == "0x2222222222222222222222222222222222222222"
    assert "private_key" not in receipt
    assert "secret" not in receipt


def test_rejects_key_shaped_signer_mode():
    from app.config import parse_signer_mode, reject_private_key_env

    with pytest.raises(ValueError, match="never a private key"):
        parse_signer_mode("0x" + "cd" * 32)
    with pytest.raises(ValueError, match="not supported"):
        reject_private_key_env({"FORT_KNOX_PRIVATE_KEY": "0xabc"})

def test_live_send_http_records_intent_no_broadcast(monkeypatch, client):
    monkeypatch.setattr(config, "LIVE_SEND", True)
    monkeypatch.setattr(config, "SIGNER_MODE", "")
    monkeypatch.setattr(config, "TREASURY_ADDRESS", "0x1111111111111111111111111111111111111111")
    r = client.post("/v1/tolls", json={"operator_id": "op", "operator_tx_id": "t-live-http"})
    assert r.status_code == 200
    data = r.json()
    assert data["live_send"] is True
    assert data["live_send_status"] == "refused_no_signer"
    assert data["live_intent"]["broadcast"] is False
    assert data["live_intent"]["asset"] == "USDC"
    assert data["live_intent"]["chain"] == "base"
    assert data["toll_usd"] == 0.002

def test_live_settle_refuses_broadcast():
    from app.live_settle import LiveSendBlocked, broadcast_usdc_base, build_usdc_base_intent

    intent = build_usdc_base_intent(to="0x1111111111111111111111111111111111111111")
    assert intent["broadcast"] is False
    assert intent["amount_units"] == 2000
    assert intent["data"].startswith("0xa9059cbb")
    with pytest.raises(LiveSendBlocked):
        broadcast_usdc_base(intent)

