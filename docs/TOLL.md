# Toll specification (MVP)

## Fee

- **Amount:** `$0.002` USD per **completed** transaction.
- **Basis:** flat; not a percentage of principal.
- **Currency of quote:** USD; settlement in crypto equivalent.
- **Who pays (MVP):** the operator running trains on the track.

## Crypto settlement options

| Option | MVP status | Notes |
|--------|------------|--------|
| **Mock ledger** | Default | In-process / SQLite receipt store. No real balances. Records toll_usd, mock crypto amount, asset symbol, and timestamp. |
| **SOL stub** | Optional | Interface + placeholder conversion; does not broadcast. |
| **ETH stub** | Optional | Same as SOL. |
| **USDC stub** | Optional | Stablecoin-shaped receipt fields; still mock unless integrated later. |

Price for mock conversion is a configurable stub rate (see app config). Do not treat mock amounts as wallet balances.

## Receipt fields

Every completed toll should produce a receipt with at least:

| Field | Description |
|-------|-------------|
| `receipt_id` | Unique receipt identifier |
| `transaction_id` | Linked track transaction |
| `operator_id` | Operator who ran the train (preferred name) |
| `partner_id` | Alias of `operator_id` (kept for API compatibility) |
| `toll_usd` | Always `0.002` for completed txs in this MVP |
| `toll_crypto_amount` | Mock (or stub) crypto quantity |
| `toll_crypto_asset` | e.g. `MOCK`, `SOL`, `ETH`, `USDC` |
| `settlement_mode` | `mock_ledger` \| `sol_stub` \| `eth_stub` \| `usdc_stub` |
| `charged_at` | ISO-8601 timestamp |
| `status` | `recorded` (MVP) |

## What we do not do in MVP

- Invent or display fake wallet balances.
- Transfer real on-chain assets.
- Net tolls against user deposits.

## Treasury (passive collection)

Operators report completed trains; tolls are meant to land at **your public treasury address**.

| Env / config | Meaning |
|--------------|---------|
| `FORT_KNOX_TREASURY_ADDRESS` | **Public** receive address only. Empty = mock meter (default). |
| `FORT_KNOX_TREASURY_CHAIN` | Hint for which rail operators should pay on (see recommendation). |
| `FORT_KNOX_SETTLEMENT_MODE` | `mock_ledger` (default) \| `usdc_stub` \| `sol_stub` \| `eth_stub` |
| `LIVE_SEND` / `FORT_KNOX_LIVE_SEND` | Hard-off (default **false**). Env-only opt-in. Records a USDC-on-Base intent; does not broadcast. |
| `FORT_KNOX_SIGNER_MODE` | Empty = refuse live send. `operator_pay` = operator sends USDC from their own wallet. Never a private key. |
| `FORT_KNOX_SIGNER_URL` | Optional external signer URL. Even if set, this build does not broadcast. |

**Never** set a private key, seed, or signing secret here. Key-shaped values are rejected.

Linking steps: [LINK-TREASURY.md](./LINK-TREASURY.md) · example: `.env.example`

## Recommended chain / token

For a flat **$0.002** USD toll:

1. **Primary:** **USDC on Base** (`FORT_KNOX_TREASURY_CHAIN=usdc_base`) — stable face value; L2 fees typically well below the toll.
2. **Alt:** **USDC on Solana** (`usdc_solana`) — same USD stability; usually cheap fees.
3. **Avoid as primary for live toll:** native SOL/ETH — price moves make “exactly $0.002” noisy; stubs remain for demos only.

Until live send is explicitly enabled, receipts only **record** the treasury address; they do not move funds. Even with `FORT_KNOX_LIVE_SEND=true` this scaffold does not broadcast — it records an intent and requires `FORT_KNOX_SIGNER_MODE=operator_pay`.
