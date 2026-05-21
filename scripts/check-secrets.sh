#!/usr/bin/env bash
# Scan tracked files for common secret patterns before git push.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Checking for secrets in tracked files..."

FAIL=0

# Block real .env files from being tracked
if git ls-files --error-unmatch backend/.env 2>/dev/null; then
  echo "ERROR: backend/.env is tracked by git — remove it."
  FAIL=1
fi
if git ls-files --error-unmatch frontend-react/.env 2>/dev/null; then
  echo "ERROR: frontend-react/.env is tracked by git — remove it."
  FAIL=1
fi

# Patterns that should not appear in committed source (exclude .env.example placeholders)
PATTERNS=(
  'hf_[A-Za-z0-9]{20,}'
  'sk-[A-Za-z0-9]{10,}'
  'postgresql://[^/\s]+:[^@\s]+@'
)

TRACKED="$(git ls-files)"
for pat in "${PATTERNS[@]}"; do
  if echo "$TRACKED" | xargs grep -lE "$pat" 2>/dev/null | grep -v '.env.example' | grep -v 'SECURITY.md' | grep -v 'check-secrets.sh' | grep -q .; then
    echo "ERROR: Possible secret matching /$pat/ in:"
    echo "$TRACKED" | xargs grep -lE "$pat" 2>/dev/null | grep -v '.env.example' | grep -v 'SECURITY.md' | grep -v 'check-secrets.sh' || true
    FAIL=1
  fi
done

# Hardcoded local DB password from old alembic.ini
if git ls-files | xargs grep -l 'abcd1234' 2>/dev/null | grep -q .; then
  echo "ERROR: Old local password 'abcd1234' still present in tracked files."
  FAIL=1
fi

if [[ "$FAIL" -eq 0 ]]; then
  echo "OK — no obvious secrets in tracked files."
  exit 0
fi

echo ""
echo "Fix issues above before pushing. See docs/SECURITY.md"
exit 1
