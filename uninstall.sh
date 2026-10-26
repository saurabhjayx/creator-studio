#!/usr/bin/env bash
# Removes a manual install (install.sh). Plugin installs: /plugin uninstall creator-studio
set -euo pipefail
DEST="${CLAUDE_HOME:-$HOME/.claude}"
rm -rf "$DEST"/skills/creator "$DEST"/skills/creator-*
rm -f "$DEST"/agents/creator-{researcher,writer,analyst,quick}.md
echo "creator-studio removed from $DEST"
