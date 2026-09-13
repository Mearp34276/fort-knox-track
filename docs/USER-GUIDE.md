# Fort Knox — Product guide

**Owner:** M.E.  
**Product:** Fort Knox Track (plugin of prebuilt tracks)  
**Status:** Demo scaffold — meters tolls; does **not** move real money until live send is explicitly enabled

---

## Deep description

### The idea in one sentence

Fort Knox is a **general-purpose plugin**: you (or any operator) download the track package, run **your own** traffic on it, and Fort Knox **passively meters** a flat **$0.002** crypto toll on every **completed** transaction.

### Why “tracks” and “trains”

| Term | Meaning |
|------|---------|
| **Plugin** | The installable package you host yourself |
| **Track** | The Fort Knox rail — routes work, assigns a route id, meters completion, triggers the toll |
| **Train** | *Your* job / transfer / cash-access hop / whatever completed work you choose to report |
| **Toll** | Flat **$0.002** USD-equivalent crypto per completed transaction |

Fort Knox does **not** own or operate the trains. Operators keep the customer relationship, the product UX, and the money movement on their side. The track only cares that a transaction **completed**, then records the toll.

### Who it’s for

**Anyone** who wants a shared metering rail for completed work — personal apps, marketplaces, banks, fintechs, or other systems. Banks and apps like MoneyLion- or Cash App–class products are **examples only**, not the product definition. The plugin is not built specifically for any one vertical.

### What you get as an operator

1. **Embeddable meter** — call `Track.report(operator_tx_id)` from Python when your side finishes a hop.
2. **HTTP inbox** — `POST /v1/tolls` with `{operator_id, operator_tx_id}` if you prefer a separate service.
3. **Optional helper API** — `POST /v1/transactions` for a richer demo (amount, purpose, fee comparison).
4. **Receipts** — each completion gets a toll receipt (`toll_usd` always `0.002` in this MVP).
5. **Idempotency** — the same `operator_id` + `operator_tx_id` (or `partner_tx_id`) returns the original record; **no double toll**.

### What Fort Knox collects

| Item | Value |
|------|--------|
| Fee | **$0.002** per completed transaction |
| Shape | Flat — **not** a % of principal |
| Who pays (MVP assumption) | The **operator** (B2B metering), not the end user’s retail balance |
| Settlement (today) | **Mock ledger** by default; stubs for USDC / SOL / ETH shaped receipts |
| Live on-chain | **Hard-off** (`LIVE_SEND` / `FORT_KNOX_LIVE_SEND` default false). Env-only opt-in; no broadcast without `FORT_KNOX_SIGNER_MODE=operator_pay` |

Recommended live rail when enabled later: **USDC on Base** (`usdc_base`). Alt: USDC on Solana. Native SOL/ETH stay demo stubs.

### Treasury (owner side)

Tolls are meant to land at a **public receive address** controlled by the project owner (M.E.):

- Config: `FORT_KNOX_TREASURY_ADDRESS` (public only) + `FORT_KNOX_TREASURY_CHAIN` (defaults to `usdc_base`)
- Empty address = mock meter still works (safe to publish / demo)
- **Never** put a private key, seed, or signing secret in config, chat, or git
- Key-shaped values are rejected by the app

### What this is not

- Not a bank, lender, or money transmitter product by itself  
- Not a consumer-facing competitor to Cash App / MoneyLion  
- Not a guarantee of fee savings (the “legacy vs track” comparison is a **demo estimate**)  
- Not authorization to move customer funds  
- Not live crypto settlement until explicitly gated on

Operators remain responsible for their own licenses, contracts, KYC/AML, and product rules. See `COMPLIANCE-NOTES.md`.

### Happy path (concept)

1. End user does something in **your** app.  
2. Your system completes that work on **your** rails.  
3. You report completion to Fort Knox (embed or HTTP).  
4. Track assigns a `track_route_id`, marks completed, charges **$0.002**.  
5. You get a receipt back; your UX continues with the end user.  
6. Fort Knox (passively) records the toll toward the configured treasury.

---

## Instructions — how to use the product

### A. Quick start (local demo)

**Requirements:** Python 3.10+, `pip`

```bash
# From the unzipped package (folder named fort-knox)
cd fort-knox
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run the API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Health check:

```bash
curl -s http://127.0.0.1:8000/health | python -m json.tool
```

You should see `status: ok`, `toll_usd: 0.002`, and treasury fields (`treasury_linked` false until an address is set).

### B. Use path 1 — Passive toll inbox (recommended for production-shaped integrations)

When **your** system finishes a transaction, report only the ids:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/tolls \
  -H "Content-Type: application/json" \
  -d '{
    "operator_id": "my-company",
    "operator_tx_id": "tx-abc-001"
  }' | python -m json.tool
```

**Response includes:** `transaction_id`, `track_route_id`, `toll_usd` (`0.002`), mock `toll_crypto`, `receipt_id`, treasury hints.

**Idempotent:** POST the same `operator_id` + `operator_tx_id` again → same record, **no second toll**.

### C. Use path 2 — Embed in Python

```python
from app.plugin import Track

track = Track(operator_id="my-company")
receipt = track.report("tx-abc-001")  # meters $0.002 once
print(receipt["toll_usd"], receipt["receipt_id"])
```

Optional: `Track(operator_id="...", settlement_mode="usdc_stub")`.

### D. Use path 3 — Full demo transaction helper

Useful for demos and fee-comparison stubs:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/transactions \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50.00,
    "currency": "USD",
    "operator_id": "demo-operator",
    "purpose": "cash_access"
  }' | python -m json.tool
```

`purpose` values: `borrow` | `cash_access` | `other`  
`partner_id` is accepted as an alias for `operator_id`.

Optional settlement modes on the request: `mock_ledger` (default), `usdc_stub`, `sol_stub`, `eth_stub`.

Lookup:

```bash
curl -s http://127.0.0.1:8000/v1/transactions/<transaction_id>
curl -s http://127.0.0.1:8000/v1/receipts/<receipt_id>
curl -s "http://127.0.0.1:8000/v1/transactions?limit=5"
```

More examples: `curl-examples.sh` (API must be running).

### E. Configure treasury (owner / publisher)

1. Copy `.env.example` → `.env`  
2. Set **only** a public address:

```bash
FORT_KNOX_TREASURY_ADDRESS=0xYourPublicBaseAddress
FORT_KNOX_TREASURY_CHAIN=usdc_base   # already the default
FORT_KNOX_SETTLEMENT_MODE=mock_ledger
```

3. Restart the API. `/health` should show `treasury_linked: true`.  
4. Live on-chain send remains **off** (`FORT_KNOX_LIVE_SEND=false`). To flip later: public treasury + `FORT_KNOX_SIGNER_MODE=operator_pay` + `FORT_KNOX_LIVE_SEND=true`. This process never holds a private key.

See [LINK-TREASURY.md](./LINK-TREASURY.md).

### F. Run tests

```bash
cd fort-knox
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

### G. What operators should tell their teams

- Fort Knox meters **completion**; you still move money on **your** rails.  
- Toll is **$0.002 flat** per completed report — plan it into your unit economics.  
- Use a stable **idempotency key** (`operator_tx_id`) so retries don’t double-charge.  
- Don’t ship private keys with the plugin.  
- Treat fee-savings fields as **demo estimates**, not SLAs.  
- Production use needs your own security review, contracts, and counsel.

---

## Doc map

| File | Contents |
|------|----------|
| [CONCEPT.md](./CONCEPT.md) | Actors, sequence, toll moment |
| [TOLL.md](./TOLL.md) | Toll math, receipts, settlement modes |
| [LINK-TREASURY.md](./LINK-TREASURY.md) | Safe wallet linking |
| [PUBLISH.md](./PUBLISH.md) | Public post checklist |
| [../COMPLIANCE-NOTES.md](../COMPLIANCE-NOTES.md) | What this is / isn’t legally |

---

*Scaffold owned by M.E.. MIT license in the package root.*
