#!/usr/bin/env bash
# Scan tracked files for secrets before git push.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Checking for secrets in tracked files..."
FAIL=0

for f in backend/.env frontend-react/.env frontend-react/.env.local .env.compose; do
  if git ls-files --error-unmatch "$f" 2>/dev/null; then
    echo "ERROR: $f is tracked — run: git rm --cached $f"
    FAIL=1
  fi
done

TRACKED="$(git ls-files)"
EXCLUDE='(\.env\.example|\.env\.compose\.example|SECURITY\.md|check-secrets\.sh|setup_database\.sh|db_url\.py|SETUP\.md)'

scan() {
  local pat="$1"
  local label="$2"
  local hits
  hits=$(echo "$TRACKED" | xargs grep -lE "$pat" 2>/dev/null | grep -Ev "$EXCLUDE" || true)
  if [[ -n "$hits" ]]; then
    echo "ERROR: $label"
    echo "$hits"
    FAIL=1
  fi
}

scan 'hf_[A-Za-z0-9]{20,}' 'Hugging Face token in tracked files'
scan 'sk-[A-Za-z0-9]{10,}' 'API key (sk-) in tracked files'
scan 'abcd1234' 'old leaked password'

# Real connection strings in code (allow only example files)
scan 'postgresql://[^/\s]+:[^@\s]+@' 'database URL with embedded password in tracked files'

if [[ "$FAIL" -eq 0 ]]; then
  echo "OK — no obvious secrets in tracked files."
  exit 0
fi

echo ""
echo "Fix issues above. See docs/SECURITY.md"
exit 1
