#!/usr/bin/env python
"""Run all track scripts to generate MIDI and WAV files."""

import importlib
import sys
from pathlib import Path


def main():
    tracks_dir = Path(__file__).parent.parent / "tracks"
    track_files = sorted(tracks_dir.glob("[0-9][0-9]_*.py"))

    if not track_files:
        print("No track scripts found in tracks/")
        sys.exit(1)

    print(f"Found {len(track_files)} tracks")

    # Add project root to path so tracks can import lib
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    for track_file in track_files:
        print(f"Generating {track_file.name}...")
        module_name = track_file.stem
        spec = importlib.util.spec_from_file_location(module_name, track_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.generate()
        print(f"  Done: {track_file.name}")

    print(f"\nAll {len(track_files)} tracks generated.")


if __name__ == "__main__":
    main()
