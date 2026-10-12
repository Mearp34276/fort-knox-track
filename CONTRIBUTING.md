# Contributing

Short path for people who clone this repo: set up, run the tests, and open a small pull request.

## Set up a dev environment

Python 3.10 or newer. Continuous integration uses Python 3.12.

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

That is the same install CI uses (`.github/workflows/ci.yml`). `requirements.txt` includes the runtime packages from `pyproject.toml` (`fastapi`, `uvicorn`, `pydantic`, `httpx`, `python-dotenv`) and `pytest`. `pyproject.toml` also lists a `dev` extra of `pytest>=8.0.0`; installing `requirements.txt` already provides it.

## Run tests

From the repository root, with the virtual environment active:

```bash
python -m pytest
```

`pytest.ini` sets `pythonpath = .`, so the `app` package imports without a separate install. CI runs this same command after `python -m pip install -r requirements.txt`.

## Report a problem

Use the issue form chooser:

https://github.com/Mearp34276/fort-knox-track/issues/new/choose

| Form | File | Use it for |
|------|------|------------|
| Bug report | `.github/ISSUE_TEMPLATE/bug_report.yml` | Something broke while installing or running the track |
| Usage question | `.github/ISSUE_TEMPLATE/usage_question.yml` | Install or usage questions |
| Commercial quote | `.github/ISSUE_TEMPLATE/commercial.yml` | Paid install help, priority support, or a custom integration |

Blank issues stay available. Leave private keys, seeds, and secrets out of issues, logs, and pull requests. Vulnerability reports go through [SECURITY.md](SECURITY.md).

## Pull requests

Keep each pull request small and limited to one change. Say what changed and why.

CI must pass. Pull requests to `main` run the workflow in `.github/workflows/ci.yml`: Python 3.12, `python -m pip install -r requirements.txt`, then `python -m pytest`.
