"""Fluidsynth wrapper for MIDI-to-WAV rendering."""

import os
import subprocess


def render_wav(mid_path: str, wav_path: str, soundfont_path: str) -> None:
    """Render a MIDI file to WAV using fluidsynth."""
    if not os.path.exists(mid_path):
        raise FileNotFoundError(f"MIDI file not found: {mid_path}")
    if not os.path.exists(soundfont_path):
        raise FileNotFoundError(f"Soundfont not found: {soundfont_path}")

    os.makedirs(os.path.dirname(wav_path) or ".", exist_ok=True)

    result = subprocess.run(
        [
            "fluidsynth",
            "-ni",
            soundfont_path,
            mid_path,
            "-F", wav_path,
            "-r", "44100",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"fluidsynth failed: {result.stderr}")
