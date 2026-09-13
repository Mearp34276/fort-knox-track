# Public post checklist — Fort Knox Plugin

Canonical package: this `fort-knox` repository.

## Product (locked)

- General-purpose **plugin tracks** — anyone can pick up
- Operators run their **own trains**
- Fort Knox **passively collects** **$0.002 crypto/tx**
- Banks/fintechs are example operators only — not the product definition
- Owner: **M.E.**

## Install surface (online pickup)

```bash
pip install -e .
# embed
from app.plugin import Track
track = Track(operator_id="my-op")
track.report("tx-123")   # meters $0.002; idempotent

# or passive HTTP inbox
uvicorn app.main:app --port 8000
# POST /v1/tolls {"operator_id":"my-op","operator_tx_id":"tx-123"}
```

## Ready locally

- [x] Embeddable `Track.report` + `POST /v1/tolls`
- [x] Mock/stub toll meter (no live keys)
- [x] README / CONCEPT / TOLL / COMPLIANCE-NOTES
- [x] MIT LICENSE + `pyproject.toml` for installable pickup
- [x] Tests green

## Before public push (owner decisions)

- [ ] Public host (e.g. GitHub) + repo name
- [ ] Fixed chain/token vs leave mode switch
- [ ] Counsel OK before live on-chain toll movement

## Do not publish as

- A bank-only or MoneyLion/Cash-App-specific product
- Live wallet keys / real balances
- Claims of underwriting or holding user funds

## Treasury (optional for mock publish)
- [x] Public-address config slot (`FORT_KNOX_TREASURY_ADDRESS`)
- [x] `.env.example` + `docs/LINK-TREASURY.md`
- [x] Live send hard-off — never ship private keys
