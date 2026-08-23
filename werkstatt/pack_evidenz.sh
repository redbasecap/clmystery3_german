#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
INNER="fall/repos/hafenkasse-versand"
git rm --cached -f "$INNER" >/dev/null 2>&1 || true
TMP="$(mktemp -d)"
mv "$INNER/.git" "$TMP/git"
git add "$INNER"
mv "$TMP/git" "$INNER/.git"
rmdir "$TMP"
echo "evidenz gepackt: $(git ls-files "$INNER" | wc -l | tr -d ' ') dateien"
