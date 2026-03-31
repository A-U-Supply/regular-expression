"""Shared CLI parser for track scripts."""

import argparse


def parse_track_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse common track script arguments."""
    parser = argparse.ArgumentParser(description="Generate a track for Regular Expression")
    parser.add_argument("--seed", type=int, default=None, help="RNG seed for variation (default: track number)")
    parser.add_argument("--no-render", action="store_true", help="Skip WAV rendering")
    return parser.parse_args(argv)
