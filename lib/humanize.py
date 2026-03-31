"""Seed-controlled humanization: timing offsets, velocity variation, strum, ghost notes."""

import pretty_midi
import numpy as np


class SeededRng:
    """Deterministic RNG wrapper for reproducible humanization."""

    def __init__(self, seed: int):
        self._rng = np.random.default_rng(seed)

    def uniform(self, low: float, high: float) -> float:
        return float(self._rng.uniform(low, high))

    def randint(self, low: int, high: int) -> int:
        return int(self._rng.integers(low, high + 1))

    def random(self) -> float:
        return float(self._rng.random())


def humanize_timing(
    notes: list[pretty_midi.Note],
    spread_ms: float = 10,
    seed: int = 0,
) -> list[pretty_midi.Note]:
    """Offset note start times by +/-spread_ms. Returns new note list."""
    rng = SeededRng(seed)
    spread_s = spread_ms / 1000.0
    result = []
    for n in notes:
        offset = rng.uniform(-spread_s, spread_s)
        new_start = max(0.0, n.start + offset)
        new_end = new_start + (n.end - n.start)
        result.append(pretty_midi.Note(
            velocity=n.velocity, pitch=n.pitch, start=new_start, end=new_end,
        ))
    return result


def humanize_velocity(
    notes: list[pretty_midi.Note],
    spread: int = 15,
    seed: int = 0,
) -> list[pretty_midi.Note]:
    """Vary note velocities by +/-spread, clamped to 1-127. Returns new note list."""
    rng = SeededRng(seed)
    result = []
    for n in notes:
        offset = rng.randint(-spread, spread)
        new_vel = max(1, min(127, n.velocity + offset))
        result.append(pretty_midi.Note(
            velocity=new_vel, pitch=n.pitch, start=n.start, end=n.end,
        ))
    return result


def strum(
    notes: list[pretty_midi.Note],
    direction: str = "down",
    spread_ms: float = 20,
) -> list[pretty_midi.Note]:
    """Stagger chord tones to simulate strumming. Down = lowest pitch first.

    Returns notes in original input order with adjusted start times.
    """
    count = len(notes)
    if count <= 1:
        return list(notes)

    # Build a pitch-order to strum-index mapping
    # "down" = lowest pitch plays first (offset 0), highest plays last
    # "up" = highest pitch plays first (offset 0), lowest plays last
    sorted_by_pitch = sorted(range(count), key=lambda i: notes[i].pitch)
    if direction == "up":
        sorted_by_pitch = list(reversed(sorted_by_pitch))

    # Use integer microsecond arithmetic to avoid float accumulation errors
    spread_us = int(spread_ms * 1000)

    # Map original index -> strum position
    strum_position = [0] * count
    for strum_idx, orig_idx in enumerate(sorted_by_pitch):
        strum_position[orig_idx] = strum_idx

    result = []
    for orig_idx, n in enumerate(notes):
        offset_us = strum_position[orig_idx] * spread_us // (count - 1)
        offset = offset_us / 1_000_000
        new_start = n.start + offset
        new_end = new_start + (n.end - n.start)
        result.append(pretty_midi.Note(
            velocity=n.velocity, pitch=n.pitch, start=new_start, end=new_end,
        ))
    return result


def ghost_notes(
    notes: list[pretty_midi.Note],
    probability: float = 0.3,
    vel_range: tuple[int, int] = (15, 40),
    seed: int = 0,
) -> list[pretty_midi.Note]:
    """Insert low-velocity ghost notes between main hits."""
    rng = SeededRng(seed)
    result = list(notes)
    sorted_notes = sorted(notes, key=lambda n: n.start)
    ghosts = []
    for i in range(len(sorted_notes) - 1):
        if rng.random() < probability:
            curr = sorted_notes[i]
            nxt = sorted_notes[i + 1]
            ghost_start = (curr.start + nxt.start) / 2.0
            ghost_dur = min(0.05, (nxt.start - curr.start) / 4.0)
            ghosts.append(pretty_midi.Note(
                velocity=rng.randint(vel_range[0], vel_range[1]),
                pitch=curr.pitch,
                start=ghost_start,
                end=ghost_start + ghost_dur,
            ))
    result.extend(ghosts)
    return result
