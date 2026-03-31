#!/usr/bin/env python
"""Concatenate all track WAVs into one album file."""

import sys
from pathlib import Path
import soundfile as sf
import numpy as np


def main():
    wav_dir = Path(__file__).parent.parent / "wav_output"
    wav_files = sorted(wav_dir.glob("[0-9][0-9]_*.wav"))

    if not wav_files:
        print("No WAV files found in wav_output/")
        sys.exit(1)

    print(f"Assembling {len(wav_files)} tracks into album...")

    chunks = []
    sample_rate = None
    for wav_file in wav_files:
        data, sr = sf.read(wav_file)
        if sample_rate is None:
            sample_rate = sr
        elif sr != sample_rate:
            print(f"Warning: {wav_file.name} has sample rate {sr}, expected {sample_rate}")
        chunks.append(data)

    album = np.concatenate(chunks)
    output_path = wav_dir / "regular_expression.wav"
    sf.write(str(output_path), album, sample_rate)
    duration = len(album) / sample_rate
    print(f"Album written to {output_path} ({duration:.1f}s)")


if __name__ == "__main__":
    main()
