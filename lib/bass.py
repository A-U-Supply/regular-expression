"""Bass line builders: kick-locked, driving eighths, counter-melody, chromatic approaches."""

import pretty_midi
from lib.melody import scale_pitches
from lib.humanize import SeededRng


def locked_bass(
    kick_times: list[float],
    root: int,
    fifth: int,
    bars: int,
    tempo: float,
    seed: int = 0,
    velocity: int = 100,
) -> list[pretty_midi.Note]:
    """Bass that follows kick ~60% of the time, drifts the other 40%."""
    rng = SeededRng(seed)
    beat_dur = 60.0 / tempo
    octave_up = root + 12
    pitch_options = [root, fifth, octave_up]
    notes = []

    for kt in kick_times:
        if rng.random() < 0.6:
            pitch = root if rng.random() < 0.7 else fifth
            dur = beat_dur * rng.uniform(0.4, 0.8)
            vel = max(1, min(127, velocity + rng.randint(-10, 10)))
            notes.append(pretty_midi.Note(velocity=vel, pitch=pitch, start=kt, end=kt + dur))
        else:
            offset = rng.uniform(-beat_dur * 0.2, beat_dur * 0.3)
            start = max(0.0, kt + offset)
            pitch = pitch_options[rng.randint(0, len(pitch_options) - 1)]
            dur = beat_dur * rng.uniform(0.3, 0.9)
            vel = max(1, min(127, velocity + rng.randint(-15, 10)))
            notes.append(pretty_midi.Note(velocity=vel, pitch=pitch, start=start, end=start + dur))
    return notes


def driving_eighths(
    root: int,
    bars: int,
    tempo: float,
    time_sig: tuple[int, int] = (4, 4),
    velocity: int = 110,
) -> list[pretty_midi.Note]:
    """Repeated eighth notes on one pitch. Wall of sound."""
    eighth_dur = 60.0 / tempo / 2.0
    total_eighths = bars * time_sig[0] * 2
    notes = []
    for i in range(total_eighths):
        start = i * eighth_dur
        notes.append(pretty_midi.Note(
            velocity=velocity, pitch=root, start=start, end=start + eighth_dur * 0.9,
        ))
    return notes


def counter_melody(
    key: str,
    mode: str,
    bars: int,
    tempo: float,
    time_sig: tuple[int, int] = (4, 4),
    seed: int = 0,
    velocity: int = 90,
) -> list[pretty_midi.Note]:
    """Wide-interval bass melody using min7, octave, tritone leaps."""
    rng = SeededRng(seed)
    available = scale_pitches(key, mode, octave=2, num_octaves=2)
    beat_dur = 60.0 / tempo
    total_beats = bars * time_sig[0]
    wide_intervals = [6, 7, 10, 12]

    notes = []
    idx = len(available) // 2
    for beat in range(total_beats):
        t = beat * beat_dur
        if rng.random() < 0.15:
            continue
        pitch = available[max(0, min(idx, len(available) - 1))]
        dur = beat_dur * rng.uniform(0.5, 0.95)
        vel = max(1, min(127, velocity + rng.randint(-15, 15)))
        notes.append(pretty_midi.Note(velocity=vel, pitch=pitch, start=t, end=t + dur))
        jump = wide_intervals[rng.randint(0, len(wide_intervals) - 1)]
        if rng.random() < 0.5:
            jump = -jump
        idx += jump
    return notes


def chromatic_approach(
    target: int,
    direction: str = "up",
    length: int = 4,
    start: float = 0.0,
    note_duration: float = 0.2,
    velocity: int = 100,
) -> list[pretty_midi.Note]:
    """Half-step slide into target pitch."""
    notes = []
    if direction == "up":
        first_pitch = target - length + 1
        for i in range(length):
            pitch = first_pitch + i
            t = start + i * note_duration
            notes.append(pretty_midi.Note(velocity=velocity, pitch=pitch, start=t, end=t + note_duration))
    else:
        first_pitch = target + length - 1
        for i in range(length):
            pitch = first_pitch - i
            t = start + i * note_duration
            notes.append(pretty_midi.Note(velocity=velocity, pitch=pitch, start=t, end=t + note_duration))
    return notes
