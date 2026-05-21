# Security checklist (before GitHub push)

## Never commit

- `backend/.env`, `frontend-react/.env`, or any file with real tokens
- Hugging Face tokens (`hf_...`)
- Database passwords in `alembic.ini` or source code
- User-uploaded PDFs/images under `backend/uploads/`
- Private keys (`.pem`, `credentials.json`)

`.gitignore` at the repo root and under `backend/` blocks these patterns.

## Already fixed in this branch

- `backend/alembic.ini` no longer contains a real `DATABASE_URL` (use `DATABASE_URL` in `.env`).
- `backend/core/security.py` reads `SECRET_KEY` from environment via `core/config.py`.
- Sample uploads removed from Git tracking (runtime data only).

## If a secret was ever committed

If you previously committed a real password or token (e.g. old `alembic.ini` with `abcd1234`):

1. **Rotate** the credential immediately (new DB password, revoke HF token).
2. **Scrub Git history** before mentors clone, or the secret remains in old commits:

   ```bash
   # Example: remove a leaked file from all history (install git-filter-repo first)
   git filter-repo --path backend/alembic.ini --invert-paths
   # Or use BFG Repo-Cleaner — see https://rtyley.github.io/bfg-repo-cleaner/
   ```

3. Force-push only if you own the repo and coordinate with collaborators.

## Mentor-safe defaults

- `PIPELINE_DRY_RUN=true` in `.env.example` — runs full UI without paid APIs.
- `docker-compose.yml` uses **dev-only** credentials (`gradeops`/`gradeops`) documented in SETUP — not production secrets.
- JWT `SECRET_KEY` must be set per machine; no shared production key in the repo.

## Pre-push script

```bash
./scripts/check-secrets.sh
```

Fix any reported issues before `git push`.
