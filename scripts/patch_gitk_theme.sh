#!/usr/bin/env bash
# Injects Solarized Dark ttk styles into the system gitk script.
# Safe to rerun — skips if the patch is already present.
# Usage: patch_gitk_theme.sh [--remove]

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
RESET='\033[0m'

info()    { echo -e "${GREEN}✓${RESET} $*"; }
warn()    { echo -e "${YELLOW}!${RESET} $*"; }
error()   { echo -e "${RED}✗${RESET} $*" >&2; }

GITK=$(which gitk)

if [[ "${1:-}" == "--remove" ]]; then
    if ! grep -q "ttk::style theme use clam" "$GITK"; then
        warn "Patch not present in $GITK — nothing to do."
        exit 0
    fi
    sudo sed -i '/# --- Solarized Dark ttk theme patch ---/,/# --- End Solarized Dark ttk theme patch ---/d' "$GITK"
    info "Patch removed from $GITK"
    exit 0
fi

if grep -q "ttk::style theme use clam" "$GITK"; then
    warn "Patch already applied to $GITK — nothing to do."
    exit 0
fi

ANCHOR="package require Tk"
if ! grep -qF "$ANCHOR" "$GITK"; then
    error "Could not find anchor line '$ANCHOR' in $GITK"
    exit 1
fi

PATCH='
# --- Solarized Dark ttk theme patch ---
ttk::style theme use clam
ttk::style configure . \
    -background #073642 \
    -foreground #839496 \
    -fieldbackground #002b36 \
    -selectbackground #073642 \
    -selectforeground #93a1a1 \
    -troughcolor #002b36 \
    -bordercolor #586e75 \
    -darkcolor #002b36 \
    -lightcolor #073642
ttk::style configure TButton \
    -background #073642 \
    -foreground #839496
ttk::style map TButton \
    -background [list active #586e75] \
    -foreground [list active #eee8d5]
ttk::style configure TScrollbar \
    -troughcolor #002b36 \
    -background #073642
ttk::style map TScrollbar \
    -background [list active #586e75]
ttk::style configure TPanedwindow \
    -background #586e75
ttk::style configure TSash \
    -sashthickness 6 \
    -background #586e75
ttk::style configure TEntry \
    -fieldbackground #002b36 \
    -foreground #839496 \
    -insertcolor #839496
ttk::style configure TLabel \
    -background #073642 \
    -foreground #839496
ttk::style configure TFrame \
    -background #073642
# --- End Solarized Dark ttk theme patch ---'

# Insert patch on the line after the anchor
sudo awk -v anchor="$ANCHOR" -v patch="$PATCH" '
    { print }
    $0 == anchor { print patch }
' "$GITK" > /tmp/gitk_patched

sudo install -m 755 /tmp/gitk_patched "$GITK"
rm /tmp/gitk_patched

info "Patch applied to $GITK"

