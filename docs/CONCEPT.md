# Fort Knox Track — Concept

## What it is

Fort Knox is a general-purpose **plugin** of prebuilt **tracks**. An operator downloads it, runs their own **trains** (traffic / jobs / transfers), and Fort Knox passively meters completion: **$0.002** crypto per completed transaction.

**Owner:** M.E..

It is not built specifically for banks or any one third-party app. Banks, fintechs, MoneyLion-class, Cash App–class, or any other product are optional examples of operators—not the product definition.

## Actors

| Actor | Role |
|-------|------|
| **Operator** | Anyone who hosts the plugin and runs trains on the track. Identified as `operator_id` (API also accepts `partner_id` as an alias). Holds the relationship with end users of *their* product. |
| **Track** | The Fort Knox rail. Routes the transaction, assigns a route id, meters completion, and triggers toll collection. |
| **Toll collector** | Component that records the $0.002 USD-equivalent crypto toll and issues a receipt. In the MVP this is a mock ledger (with optional SOL/ETH/USDC stubs). |
| **End user** | Consumer of the operator’s product. Does not interact with Fort Knox directly in this model. |

## Happy-path sequence

1. End user initiates an action in the operator’s app or system (any completed work the operator chooses to send over the track).
2. Operator calls Fort Knox Track: `POST /v1/transactions` with amount, currency, `operator_id` (or `partner_id`), and purpose.
3. Track validates the request, creates a transaction record, assigns a `track_route_id`.
4. Track marks the transaction **completed** (MVP: synchronous success; production would await settlement confirmations).
5. On completion, Toll collector charges **$0.002** USD equivalent in crypto and writes a receipt.
6. Track returns transaction id, status, toll details, route id, and an estimated fee comparison (demo only).
7. Operator continues its own product UX with the end user.

## Where the toll is charged

- **Event:** completed transaction on the track.
- **Payer (MVP assumption):** the operator (B2B metering), not the end user retail balance.
- **Amount:** fixed $0.002 USD equivalent per completed tx.
- **Not charged on:** rejected or failed validation requests (no completed transaction).

## Assumptions (MVP)

- Operators remain responsible for their own products, licenses, and user relationships; Fort Knox does not underwrite or lend.
- Currency in the demo is treated as a label; no FX engine.
- Completion is immediate for demo purposes.
- Toll crypto amounts use a mock price feed; no real chain submission unless a stub is explicitly wired.
- Fee “savings” vs legacy rails are **estimates labeled as demo**—not guarantees.
