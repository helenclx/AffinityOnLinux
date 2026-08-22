#!/bin/bash
# Manually hand an affinity:// OAuth callback URL to Affinity, bypassing the
# OS-level "Open Affinity?" protocol-handler confirmation dialog entirely.
#
# Use this if the browser-to-Affinity handoff isn't completing on its own
# (for example, while testing a fresh Wine prefix, or if your desktop's
# protocol-handler dialog isn't wired up yet). With LoginFix installed and
# working normally, you should not need this, sign-in completes on its own.
#
# Get the callback URL from your browser's address bar (or via "copy link"
# on the "Open Affinity?" page) right before it would normally hand off to
# Affinity, then paste it here. The pasted value is never echoed, never
# written to disk, and never touches shell history (read -s, not a typed
# command).
set -euo pipefail

WINEPREFIX="${WINEPREFIX:-$HOME/.affinity}"
WINE_BIN="${WINE_BIN:-wine}"

read -rs -p "Paste the affinity:// callback URL, then press Enter: " CALLBACK_URL
echo
echo

if [[ "$CALLBACK_URL" != affinity://* ]]; then
    echo "That doesn't look like an affinity:// URL. Aborting." >&2
    exit 1
fi

echo "Invoking Wine with the callback..."
WINEPREFIX="$WINEPREFIX" "$WINE_BIN" start "$CALLBACK_URL"
