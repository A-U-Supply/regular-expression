#!/usr/bin/env bash
set -euo pipefail

SOUNDFONT_DIR="soundfonts"
SOUNDFONT_FILE="$SOUNDFONT_DIR/FluidR3_GM.sf2"

if [ -f "$SOUNDFONT_FILE" ]; then
    echo "Soundfont already exists at $SOUNDFONT_FILE"
    exit 0
fi

mkdir -p "$SOUNDFONT_DIR"

# Download SGM (Shan's GM Soundfont) from Internet Archive — good quality, 236MB
echo "Downloading SGM-V2.01 soundfont from Internet Archive..."
TMPDIR=$(mktemp -d)
ia download "SGM-V2.01" "SGM-V2.01.sf2" --destdir="$TMPDIR"
cp "$TMPDIR/SGM-V2.01/SGM-V2.01.sf2" "$SOUNDFONT_FILE"
rm -rf "$TMPDIR"
echo "Soundfont installed at $SOUNDFONT_FILE"
