"""Melody contour builders, phrase generators, spikes, stutters, broken trails."""

import pretty_midi
from lib.constants import SCALES
from lib.humanize import SeededRng

# Interval name to semitones for spike()
_SPIKE_INTERVALS = {
    "min2": 1, "maj2": 2, "min3": 3, "maj3": 4,
    "P4": 5, "tritone": 6, "P5": 7,
    "min6": 8, "maj6": 9, "min7": 10, "maj7": 11,
    "octave": 12,
}

_NOTE_TO_PC = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
    "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
}


def scale_pitches(
    key: str,
    mode: str,
    octave: int = 4,
    num_octaves: int = 1,
) -> list[int]:
    """Get MIDI pitches for a scale across octaves."""
    root_name = key.rstrip("m")
    root_pc = _NOTE_TO_PC[root_name]
    base_midi = root_pc + (octave + 1) * 12
    intervals = SCALES[mode]
    pitches = []
    for oct in range(num_octaves):
        for iv in intervals:
            pitches.append(base_midi + iv + oct * 12)
    return pitches


def contour(
    key: str,
    mode: str,
    direction: str = "descending",
    num_notes: int = 8,
    octave: int = 4,
    seed: int = 0,
    start_time: float = 0.0,
    note_duration: float = 0.25,
    note_gap: float = 0.1,
    velocity: int = 90,
) -> list[pretty_midi.Note]:
    """Generate a melodic contour within scale constraints."""
    rng = SeededRng(seed)
    available = scale_pitches(key, mode, octave=octave, num_octaves=2)

    if direction == "descending":
        start_idx = len(available) - 1 - rng.randint(0, 3)
    else:
        start_idx = rng.randint(0, 3)

    notes = []
    idx = start_idx
    t = start_time
    for i in range(num_notes):
        pitch = available[max(0, min(idx, len(available) - 1))]
        notes.append(pretty_midi.Note(
            velocity=velocity, pitch=pitch, start=t, end=t + note_duration,
        ))
        t += note_duration + note_gap
        if direction == "descending":
            step = -rng.randint(1, 2) if rng.random() < 0.75 else rng.randint(1, 2)
        else:
            step = rng.randint(1, 2) if rng.random() < 0.75 else -rng.randint(1, 2)
        idx += step
    return notes


def phrase(
    key: str,
    mode: str,
    bars: int,
    tempo: float,
    time_sig: tuple[int, int],
    density: float = 0.6,
    seed: int = 0,
    velocity: int = 90,
) -> list[pretty_midi.Note]:
    """Generate an asymmetric melodic phrase with gaps."""
    rng = SeededRng(seed)
    available = scale_pitches(key, mode, octave=4, num_octaves=2)
    beats_per_bar = time_sig[0]
    beat_duration = 60.0 / tempo
    total_beats = bars * beats_per_bar

    notes = []
    idx = len(available) // 2
    for beat in range(total_beats):
        t = beat * beat_duration
        if rng.random() > density:
            continue
        pitch = available[max(0, min(idx, len(available) - 1))]
        dur = beat_duration * rng.uniform(0.4, 0.9)
        vel = max(1, min(127, velocity + rng.randint(-20, 20)))
        notes.append(pretty_midi.Note(velocity=vel, pitch=pitch, start=t, end=t + dur))
        idx += rng.randint(-2, 2)
    return notes


def spike(
    base_pitch: int,
    interval: str = "min7",
    start: float = 0.0,
    velocity: int = 100,
    leap_duration: float = 0.15,
    drop_duration: float = 0.3,
) -> list[pretty_midi.Note]:
    """Leap up by interval then immediate drop back to base. Returns 2 notes."""
    semitones = _SPIKE_INTERVALS[interval]
    high_pitch = base_pitch + semitones
    return [
        pretty_midi.Note(velocity=velocity, pitch=high_pitch, start=start, end=start + leap_duration),
        pretty_midi.Note(velocity=velocity, pitch=base_pitch, start=start + leap_duration, end=start + leap_duration + drop_duration),
    ]


def stutter(
    pitch: int,
    count: int,
    note_duration: float = 0.1,
    gap: float = 0.05,
    start: float = 0.0,
    velocity: int = 90,
) -> list[pretty_midi.Note]:
    """Obsessive single-note repetition."""
    notes = []
    t = start
    for _ in range(count):
        notes.append(pretty_midi.Note(velocity=velocity, pitch=pitch, start=t, end=t + note_duration))
        t += note_duration + gap
    return notes


def broken_trail(
    notes: list[pretty_midi.Note],
    decay_point: int,
) -> list[pretty_midi.Note]:
    """Phrase that trails into nothing. Notes after decay_point fade in velocity."""
    result = []
    remaining = len(notes) - decay_point
    for i, n in enumerate(notes):
        if i < decay_point:
            result.append(pretty_midi.Note(velocity=n.velocity, pitch=n.pitch, start=n.start, end=n.end))
        else:
            fade = max(1, int(n.velocity * (1.0 - (i - decay_point + 1) / (remaining + 1))))
            result.append(pretty_midi.Note(velocity=fade, pitch=n.pitch, start=n.start, end=n.end))
    return result
