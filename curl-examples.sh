#!/usr/bin/env bash
# Fort Knox Track — curl examples (API must be running on :8000)
set -euo pipefail
BASE="${BASE_URL:-http://127.0.0.1:8000}"

echo "== Health =="
curl -s "$BASE/health" | python -m json.tool

echo
echo "== Create cash_access transaction (mock ledger) =="
curl -s -X POST "$BASE/v1/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50.00,
    "currency": "USD",
    "operator_id": "demo-operator",
    "purpose": "cash_access"
  }' | python -m json.tool

echo
echo "== Create borrow transaction with SOL stub =="
RESP=$(curl -s -X POST "$BASE/v1/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 200.00,
    "currency": "USD",
    "operator_id": "demo-operator-2",
    "purpose": "borrow",
    "settlement_mode": "sol_stub"
  }')
echo "$RESP" | python -m json.tool
TX_ID=$(echo "$RESP" | python -c "import sys,json; print(json.load(sys.stdin)['transaction_id'])")
RCPT_ID=$(echo "$RESP" | python -c "import sys,json; print(json.load(sys.stdin)['receipt_id'])")

echo
echo "== Get transaction $TX_ID =="
curl -s "$BASE/v1/transactions/$TX_ID" | python -m json.tool

echo
echo "== Get receipt $RCPT_ID =="
curl -s "$BASE/v1/receipts/$RCPT_ID" | python -m json.tool

echo
echo "== List recent transactions =="
curl -s "$BASE/v1/transactions?limit=5" | python -m json.tool

# Passive toll inbox (plugin meter)
curl -s -X POST "$BASE/v1/tolls" \
  -H "Content-Type: application/json" \
  -d '{"operator_id":"demo-operator","operator_tx_id":"op-tx-001"}' | python -m json.tool
