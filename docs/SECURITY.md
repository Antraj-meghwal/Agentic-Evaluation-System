# Security — never commit credentials

## Files that must stay local (gitignored)

| File | Purpose |
|------|---------|
| `backend/.env` | API secrets, `DATABASE_URL`, `HF_TOKEN`, `SECRET_KEY` |
| `frontend-react/.env.local` | `VITE_API_URL` |
| `.env.compose` | Docker Postgres password |
| `backend/uploads/*` | Exam PDFs (student data) |

Copy examples only:

```bash
cp backend/.env.example backend/.env
cp frontend-react/.env.example frontend-react/.env.local
cp .env.compose.example .env.compose
```

## Before every `git push`

```bash
./scripts/check-secrets.sh
git status   # must NOT list .env or .env.compose
```

## No hardcoded secrets in Python

- `backend/core/db_url.py` reads `DATABASE_URL` or `POSTGRES_*` from `.env` only.
- `alembic.ini` has no database URL.
- JWT `SECRET_KEY` and `HF_TOKEN` come from environment only.

## Docker dev passwords

`docker-compose.yml` loads `.env.compose` (gitignored). The example file uses shared **dev-only** values for local machines — not for production.

## If you ever committed a real token or password

1. Revoke/rotate it immediately.
2. Old commits still contain it — use [git-filter-repo](https://github.com/newren/git-filter-repo) or BFG before making the repo public.
