# Publish checklist — Fort Knox (GitHub)

Owner: M.E.. Package is MIT-licensed; product is a general-purpose track plugin ($0.002 crypto toll per completed transaction). Anyone runs their own trains; banks/fintechs are examples only.

## 1. Create the GitHub repo

1. On GitHub, create a **new empty repository** (no README/LICENSE auto-init if you already have them in this tree).
2. Choose visibility (public for online pickup).
3. Note the remote URL GitHub shows (HTTPS or SSH). Do not invent a URL—use the one GitHub gives you.

## 2. Push this tree

From the unpacked project root (this folder after unzip, or a clone):

```bash
git init
git add .
git commit -m "Initial public release: Fort Knox track plugin"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

Replace `<YOUR_GITHUB_REPO_URL>` with the URL from step 1.

## 3. Attach a release zip (optional but recommended)

1. On GitHub: **Releases → Create a new release**.
2. Tag e.g. `v0.1.0`, title matching the version in `pyproject.toml`.
3. Upload `fort-knox-public.zip` (or `dist/fort-knox-plugin.zip`) as a release asset.
4. Publish the release.

Operators can then clone the repo or download the zip from the release page.

## 4. Sanity after publish

- [ ] README renders; LICENSE is MIT; docs link works
- [ ] No `.venv`, `__pycache__`, `.pytest_cache`, or local secrets in the tree
- [ ] `pip install -e .` and `pytest` succeed for a fresh clone
- [ ] No live wallet keys or claims of licensed money transmission

## Out of scope until counsel

Live on-chain toll settlement; production operator contracts; regulatory licensing.
