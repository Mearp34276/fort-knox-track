# GitHub pickup

After cloning or unzipping the public package:

```bash
cd fort-knox
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
uvicorn app.main:app --reload --port 8000
```

Embed: `from app.plugin import Track` then `track.report(operator_tx_id)`.

Meters **$0.002** crypto per completed transaction (mock/stub only). No live on-chain settlement in this package.

Full publish steps: see `PUBLISH-CHECKLIST.md` at the repo root (create empty GitHub repo, push, optional release zip). Use the remote URL GitHub gives you—do not invent one.
