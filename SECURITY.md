# Security

## Report a vulnerability

Report a vulnerability privately with GitHub private vulnerability reporting (Security Advisories) for this repository:

https://github.com/Mearp34276/fort-knox-track/security/advisories/new

On the repository **Security** tab, choose **Report a vulnerability**. The report stays in a private security advisory. Include what you can about impact and how to reproduce it, with secrets removed.

This repository has no security email address. Public issues are for bugs and usage questions ([CONTRIBUTING.md](CONTRIBUTING.md)).

## Supported versions

| Version | Supported |
|---------|-----------|
| [v0.1.0](https://github.com/Mearp34276/fort-knox-track/releases/tag/v0.1.0) | Yes |
| `main` | Yes |

The package version in `pyproject.toml` is `0.1.0`. Fixes for supported versions land on `main`.

## Mock toll by default

The toll is a mock ledger by default. `DEFAULT_SETTLEMENT_MODE` in `app/config.py` is `mock_ledger`.

Live sending is off unless an operator explicitly enables it. `LIVE_SEND` and `FORT_KNOX_LIVE_SEND` are environment-only and default to false (`app/config.py`). When that flag is on, `app/live_send.py` records a transfer intent and does not broadcast a transaction.
