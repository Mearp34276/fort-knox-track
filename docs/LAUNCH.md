# Launch posts (drafts — not posted)

**Owner:** M.E.

Paste-ready copy for one Show HN and one short Reddit / Indie Hackers-style post. **Nothing here is published** until M.E. pastes it. This file is not a launch announcement and not evidence of traffic, signups, or revenue.

## Honesty (do not soften when pasting)

- **No income guarantees.** Free MIT use is the product. A commercial quote is optional paid work a buyer requests. It is not a promise that anyone earns money.
- **$0.002 is product design, not cash received.** The track meters a disclosed **$0.002** USDC-on-Base toll when a train completes. That figure is the spec. It is not money that has landed. Until a buyer pays, reported revenue is **$0**.
- **Mock meter is the default.** The public package does not ship private keys. **`LIVE_SEND` / live settlement stays hard-off** and is not claimed live. Even if an operator later opts in, this scaffold records an intent; it does not broadcast.
- **Sponsors is not live.** `https://github.com/sponsors/Mearp34276` is a placeholder until GitHub approves Sponsors on the owner account. Do not say the project is receiving sponsor money.
- **No live public demo.** Checked 2026-09-24: `https://fort-knox-track.fly.dev` does not resolve. Do not claim that host is up. Run the API locally (`uvicorn` on `127.0.0.1`).
- **No metrics.** Do not add stars, users, revenue, or “$100/day” to these posts.
- **General-purpose tracks.** Operators run their own trains. Banks and fintechs are examples only, not the product definition. Not a gambling product.

Repo: https://github.com/Mearp34276/fort-knox-track

Commercial quote Issue (template `commercial.yml`, label `commercial`):  
https://github.com/Mearp34276/fort-knox-track/issues/new?template=commercial.yml

## Show HN

**Title**

```
Show HN: Fort Knox – tracks you install, trains you run, mock $0.002 toll
```

**URL**

```
https://github.com/Mearp34276/fort-knox-track
```

**Text**

```
Fort Knox is a small MIT plugin of tracks. You install the track. You run the trains — a job, transfer, or any completed transaction in your own product. Fort Knox does not run the trains and does not hold the customer relationship or the money movement. You report when a train has completed.

When a train completes, the track assigns a route id, writes a receipt, and meters a disclosed $0.002 USDC-on-Base toll. That $0.002 figure is product design. It is not cash this project has received. The public package uses a mock meter by default: no private keys and no live sends. LIVE_SEND stays hard-off.

Same operator id + transaction id returns the same receipt. Reporting again does not meter a second toll.

This post does not claim a live public demo. https://fort-knox-track.fly.dev does not resolve (checked 2026-09-24). Install and run it locally.

What it is not: a bank, a money-transmitter license, a gambling product, or guaranteed income. Free MIT use needs nothing else. Operators own their compliance.

Owner: M.E.
Repo: https://github.com/Mearp34276/fort-knox-track

Paid install help, priority support, or a one-off operator integration is optional. Open a Commercial quote Issue (free use does not require this):
https://github.com/Mearp34276/fort-knox-track/issues/new?template=commercial.yml

Install/help quotes are often $150–$500 after you describe the job. That is a range for work someone asks for, not a guarantee that anyone earns it.

GitHub Sponsors for Mearp34276 is not live until GitHub approves the account. This project is not receiving sponsor money.
```

## Reddit / Indie Hackers (one short post)

Use this as a single post (Side Project, Indie Hackers, or similar). Do not post it twice as if they were different launches.

**Title**

```
Plugin tracks for completed work (MIT) — you run the trains; mock $0.002 toll by default
```

**Text**

```
Fort Knox is a free MIT plugin of tracks. You install the rail. You run your own trains (jobs, transfers, or other completed transactions in your product). Fort Knox does not operate the trains.

Report a completion and get an idempotent receipt. The same operator + transaction id returns the same receipt, so retries do not double-meter. The disclosed toll is $0.002 USDC on Base per completed train. That number is the product spec, not cash received. The default meter is mock: no private keys, and LIVE_SEND stays hard-off.

There is no live public demo. https://fort-knox-track.fly.dev does not resolve (checked 2026-09-24). Run it on localhost.

Owner: M.E.
License: MIT
Repo: https://github.com/Mearp34276/fort-knox-track

Paid install / support quote (optional; free use stays free):
https://github.com/Mearp34276/fort-knox-track/issues/new?template=commercial.yml

No income guarantees. GitHub Sponsors on Mearp34276 is not live until GitHub approves it. This post is not a claim that the project is earning money.
```
