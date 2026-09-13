# Link your treasury (passive toll collection)

Fort Knox meters **$0.002 crypto per completed transaction**. To collect for real, operators need a place to send that toll: **your public treasury address**.

## Safe linking rules

1. Share only a **public** wallet address (the receive address).
2. **Never** put a private key, seed phrase, or exchange password in chat, `.env`, GitHub, or this repo.
3. Prefer a wallet you control (hardware or software). Exchange deposit addresses can work but are easier to mess up (memo/tag networks).
4. Start on **testnet / mock** until the address is confirmed in a dry run.

## Recommended setup (for a $0.002 toll)

| Choice | Why |
|--------|-----|
| **USDC on Base** (locked default) | Stable $0.002; L2 fees usually well below the toll |
| **USDC on Solana** (alt) | Same stable face value if you prefer Solana |
| Your own wallet receive address | You control withdrawals |

SOL or ETH stubs exist in the demo but stablecoin USDC is usually cleaner for a flat USD-priced toll.

## Steps

1. You create (or pick) a wallet and copy the **public receive address**.
2. Put only the **public** address in `.env` as `FORT_KNOX_TREASURY_ADDRESS` (chain defaults to `usdc_base`).
3. Restart the API and check `/health` shows `treasury_linked: true`.
4. Run a mock/dry-run toll report — receipts should name that address.
5. Live on-chain settlement stays off (`FORT_KNOX_LIVE_SEND=false`). Flip later only after counsel: set a public treasury address, `FORT_KNOX_SIGNER_MODE=operator_pay`, then `FORT_KNOX_LIVE_SEND=true`. This process never holds a private key; the operator pays USDC on Base from a wallet they control. The scaffold records the intent and does not broadcast.

## Config

See `.env.example`. Empty treasury = mock ledger only (safe to publish).

## Flip live later (env only)

```bash
# Public address only — never a key
FORT_KNOX_TREASURY_ADDRESS=0xYourPublicBaseAddress
FORT_KNOX_TREASURY_CHAIN=usdc_base
FORT_KNOX_SIGNER_MODE=operator_pay
# optional: FORT_KNOX_SIGNER_URL=https://your-signer.example
FORT_KNOX_LIVE_SEND=true
```

Without `operator_pay`, live mode refuses the send (intent is recorded as `refused_no_signer`).
