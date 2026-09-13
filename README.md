# Fort Knox

Fort Knox is an installable **plugin of tracks**. Think of it like a railroad:

- A **track** is the Fort Knox rail you install — the shared path that accepts completed work, assigns a route id, and meters a toll.
- A **train** is *your* traffic on that rail — a job, transfer, cash-access hop, borrow flow, or any completed transaction **you** run in **your** product.
- Fort Knox does **not** run the trains. You (the operator) keep the customer relationship and the money movement; you only **report** when a train has completed on the track.
- When a train completes, Fort Knox **passively meters a disclosed $0.002 USDC (Base) toll** and issues a receipt.

The public package ships with a **mock meter** by default — no private keys, no live sends. Operators configure a public treasury address when ready; live settlement stays off until enabled.

**Owner:** M.E.

## Product

| Piece | Meaning |
|-------|---------|
| **Plugin** | The installable package you host yourself |
| **Track** | The Fort Knox rail: routes completed work, meters completion, records the toll |
| **Train** | Your own traffic on that rail (jobs / transfers / completed transactions you operate) |
| **Operator** | Anyone who installs the plugin and runs their own trains |
| **Toll** | Flat **$0.002** USD-equivalent crypto per **completed** train/transaction |

**In short:** tracks = the rails (Fort Knox). trains = the traffic (yours). toll = $0.002 when a train finishes.

Optional examples of who might run trains (not required, not exclusive): personal apps, marketplaces, banks, or fintechs such as MoneyLion- or Cash App–class products. Those are illustrations only—the track is general-purpose.

| Item | Value |
|------|--------|
| Fee | **$0.002** per completed transaction |
| Settlement | Crypto equivalent (default: **mock ledger**; live USDC-on-Base is scaffolded but **hard-off**) |
| When charged | On successful completion of a transaction on the track |

There is no percentage take of principal in this MVP—only the flat per-transaction toll.

## Operator instructions

### Install

Python 3.10+ and `pip`:

```bash
cd fort-knox
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Report a completed train

**HTTP inbox** — `POST /v1/tolls`:

```bash
curl -s -X POST http://127.0.0.1:8000/v1/tolls \
  -H "Content-Type: application/json" \
  -d '{"operator_id":"demo-operator","operator_tx_id":"op-tx-001"}' | python -m json.tool
```

**Embed** — `Track.report`:

```python
from app.plugin import Track

track = Track(operator_id="demo-operator")
receipt = track.report("op-tx-001")  # meters $0.002 once; idempotent
```

Same `operator_id` + `operator_tx_id` returns the original receipt (no second toll).

Optional helper for demos: `POST /v1/transactions` (amount, purpose, fee comparison). `partner_id` aliases `operator_id`. More examples: `curl-examples.sh` and `tests/`.

## What’s in this repo

- Embeddable plugin: `from app.plugin import Track` then `track.report(operator_tx_id)`
- Passive toll inbox: `POST /v1/tolls` `{operator_id, operator_tx_id}`
- Optional local helper: `POST /v1/transactions`
- In-memory store (optional SQLite later)
- Mock toll ledger + USDC-on-Base live-intent scaffold (hard-off)
- Fee optimizer stub (legacy estimate vs track + toll)
- Concept, toll, and compliance notes under `docs/`

This is a **demo scaffold**. It does not move real money unless live send is explicitly enabled by the operator (off by default, and even then it only records an intent).

## Treasury (public address only)

Passive tolls can be aimed at a receive address. **Never** put a private key in `.env`, chat, or git. `.env` is gitignored.

1. Recommended rail: **USDC on Base** (alt: USDC on Solana).
2. Copy only the **public** address into `.env` (see `.env.example`). Public defaults leave the address **empty**.
3. Set `FORT_KNOX_TREASURY_ADDRESS` (public only). Chain defaults to `usdc_base`.
4. Mock meter works with an empty address. **`LIVE_SEND` / `FORT_KNOX_LIVE_SEND` default false.**

To flip live later (env only, after counsel): set a public treasury address, `FORT_KNOX_SIGNER_MODE=operator_pay` (operator sends USDC from their own wallet — this process never holds a key), then `FORT_KNOX_LIVE_SEND=true`. The scaffold records a USDC-on-Base intent; it does not broadcast.

Full steps: [docs/LINK-TREASURY.md](docs/LINK-TREASURY.md) · toll spec: [docs/TOLL.md](docs/TOLL.md)


## Docs

| File | Contents |
|------|----------|
| [docs/USER-GUIDE.md](docs/USER-GUIDE.md) | Deep product description + how to use |
| [docs/CONCEPT.md](docs/CONCEPT.md) | Actors, happy path, where toll is charged |
| [docs/TOLL.md](docs/TOLL.md) | Toll math, settlement options, receipt fields |
| [COMPLIANCE-NOTES.md](COMPLIANCE-NOTES.md) | What this is / isn’t from a regulatory standpoint |

## License / packaging

Scaffold owned by M.E. MIT license in `LICENSE`. See [docs/PUBLISH.md](docs/PUBLISH.md) and [PUBLISH-CHECKLIST.md](PUBLISH-CHECKLIST.md).

## Compliance note

**This is a technical meter/plugin scaffold — not a money-transmitter license, banking charter, or legal advice. Operators own their compliance; live crypto settlement stays off until the owner enables it under counsel.**


## Report concerns

Open a free GitHub Issue: https://github.com/Mearp34276/fort-knox-track/issues

We watch Issues on weekdays and update the software when people report problems or confusion. No paid support plan.
