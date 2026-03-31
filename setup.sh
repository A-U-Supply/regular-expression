#!/usr/bin/env bash
set -euo pipefail

SOUNDFONT_DIR="soundfonts"
SOUNDFONT_FILE="$SOUNDFONT_DIR/FluidR3_GM.sf2"
SOUNDFONT_URL="https://keymusician01.s3.amazonaws.com/FluidR3_GM.zip"

if [ -f "$SOUNDFONT_FILE" ]; then
    echo "Soundfont already exists at $SOUNDFONT_FILE"
    exit 0
fi

mkdir -p "$SOUNDFONT_DIR"
echo "Downloading FluidR3_GM soundfont..."
curl -L -o "$SOUNDFONT_DIR/FluidR3_GM.zip" "$SOUNDFONT_URL"
unzip -o "$SOUNDFONT_DIR/FluidR3_GM.zip" -d "$SOUNDFONT_DIR"
rm "$SOUNDFONT_DIR/FluidR3_GM.zip"
echo "Soundfont installed at $SOUNDFONT_FILE"
