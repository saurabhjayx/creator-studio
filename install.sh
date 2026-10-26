#!/usr/bin/env bash
# Manual install (no plugin system): copies skills, agents and scripts into ~/.claude.
# Preferred install is the plugin marketplace, see README.
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
DEST="${CLAUDE_HOME:-$HOME/.claude}"

command -v python3 >/dev/null || { echo "python3 (3.9+) required"; exit 1; }
mkdir -p "$DEST/skills" "$DEST/agents"

for d in "$SRC"/skills/*/; do
  name="$(basename "$d")"
  rm -rf "$DEST/skills/$name"
  cp -R "$d" "$DEST/skills/$name"
done
cp "$SRC"/agents/*.md "$DEST/agents/"

echo "Installed $(ls -d "$SRC"/skills/*/ | wc -l | tr -d ' ') skills and $(ls "$SRC"/agents/*.md | wc -l | tr -d ' ') agents into $DEST"
echo "Restart Claude Code, then try: /creator trends"
