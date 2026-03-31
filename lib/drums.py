"""Drum pattern builders with humanized timing."""

import pretty_midi
from lib.constants import (
    KICK, SNARE, HAT_CLOSED, HAT_OPEN, FLOOR_TOM, RACK_TOM, CRASH,
)
from lib.humanize import SeededRng


def _drum_note(pitch: int, start: float, duration: float = 0.1, velocity: int = 100) -> pretty_midi.Note:
    return pretty_midi.Note(velocity=velocity, pitch=pitch, start=start, end=start + duration)


def driving_emo(
    bars: int,
    tempo: float,
    time_sig: tuple[int, int] = (4, 4),
    seed: int = 0,
) -> list[pretty_midi.Note]:
    """Kick 1+3, snare 2+4, 8th-note hats. Humanized timing and velocity."""
    rng = SeededRng(seed)
    beat_dur = 60.0 / tempo
    eighth = beat_dur / 2.0
    beats_per_bar = time_sig[0]
    notes = []

    for bar in range(bars):
        bar_start = bar * beats_per_bar * beat_dur
        for beat in range(beats_per_bar):
            t = bar_start + beat * beat_dur
            if beat % 2 == 0:
                offset = rng.uniform(-0.005, 0.005)
                notes.append(_drum_note(KICK, max(0.0, t + offset), velocity=100 + rng.randint(-8, 8)))
            if beat % 2 == 1:
                offset = rng.uniform(-0.005, 0.005)
                notes.append(_drum_note(SNARE, max(0.0, t + offset), velocity=100 + rng.randint(-8, 8)))
                if rng.random() < 0.3:
                    ghost_t = max(0.0, t - eighth * 0.5 + rng.uniform(-0.005, 0.005))
                    notes.append(_drum_note(SNARE, ghost_t, velocity=rng.randint(15, 35)))
            for sub in range(2):
                ht = t + sub * eighth + rng.uniform(-0.005, 0.005)
                hat_vel = rng.randint(50, 110)
                hat_pitch = HAT_OPEN if (sub == 1 and rng.random() < 0.2) else HAT_CLOSED
                notes.append(_drum_note(hat_pitch, max(0.0, ht), velocity=hat_vel))
    return notes


def blast(
    bars: int,
    tempo: float,
    time_sig: tuple[int, int] = (4, 4),
    seed: int = 0,
) -> list[pretty_midi.Note]:
    """Kick+snare alternating on 16ths. Capped at 4 bars."""
    rng = SeededRng(seed)
    bars = min(bars, 4)
    sixteenth = 60.0 / tempo / 4.0
    beats_per_bar = time_sig[0]
    total_sixteenths = bars * beats_per_bar * 4
    notes = []

    for i in range(total_sixteenths):
        t = i * sixteenth + rng.uniform(-0.005, 0.005)
        t = max(0.0, t)
        vel = 100 + rng.randint(-10, 10)
        if i % 2 == 0:
            notes.append(_drum_note(KICK, t, velocity=vel))
        else:
            notes.append(_drum_note(SNARE, t, velocity=vel))
    return notes


def half_time(
    bars: int,
    tempo: float,
    time_sig: tuple[int, int] = (4, 4),
    seed: int = 0,
) -> list[pretty_midi.Note]:
    """Snare on beat 3 only. Cavernous."""
    rng = SeededRng(seed)
    beat_dur = 60.0 / tempo
    beats_per_bar = time_sig[0]
    notes = []

    for bar in range(bars):
        bar_start = bar * beats_per_bar * beat_dur
        for beat in range(beats_per_bar):
            t = bar_start + beat * beat_dur
            if beat == 0:
                offset = rng.uniform(-0.005, 0.005)
                notes.append(_drum_note(KICK, max(0.0, t + offset), velocity=100 + rng.randint(-8, 8)))
            if beat == 2:
                offset = rng.uniform(-0.005, 0.005)
                notes.append(_drum_note(SNARE, max(0.0, t + offset), velocity=110 + rng.randint(-5, 5)))
            if rng.random() < 0.6:
                offset = rng.uniform(-0.005, 0.005)
                notes.append(_drum_note(HAT_CLOSED, max(0.0, t + offset), velocity=rng.randint(40, 80)))
    return notes


def floor_tom_pulse(
    bars: int,
    tempo: float,
    time_sig: tuple[int, int] = (4, 4),
    seed: int = 0,
) -> list[pretty_midi.Note]:
    """Floor tom replaces kick. No kick in this pattern."""
    rng = SeededRng(seed)
    beat_dur = 60.0 / tempo
    beats_per_bar = time_sig[0]
    notes = []

    for bar in range(bars):
        bar_start = bar * beats_per_bar * beat_dur
        for beat in range(beats_per_bar):
            t = bar_start + beat * beat_dur
            if beat % 2 == 0:
                offset = rng.uniform(-0.005, 0.005)
                notes.append(_drum_note(FLOOR_TOM, max(0.0, t + offset), velocity=95 + rng.randint(-10, 10)))
            offset = rng.uniform(-0.005, 0.005)
            notes.append(_drum_note(HAT_CLOSED, max(0.0, t + offset), velocity=rng.randint(50, 90)))
    return notes


def no_snare(
    bars: int,
    tempo: float,
    time_sig: tuple[int, int] = (4, 4),
    seed: int = 0,
) -> list[pretty_midi.Note]:
    """Kick, hat, toms only. Anxious."""
    rng = SeededRng(seed)
    beat_dur = 60.0 / tempo
    eighth = beat_dur / 2.0
    beats_per_bar = time_sig[0]
    notes = []

    for bar in range(bars):
        bar_start = bar * beats_per_bar * beat_dur
        for beat in range(beats_per_bar):
            t = bar_start + beat * beat_dur
            if beat % 2 == 0:
                offset = rng.uniform(-0.005, 0.005)
                notes.append(_drum_note(KICK, max(0.0, t + offset), velocity=95 + rng.randint(-8, 8)))
            if rng.random() < 0.3:
                offset = rng.uniform(-0.005, 0.005)
                notes.append(_drum_note(RACK_TOM, max(0.0, t + offset), velocity=rng.randint(60, 90)))
            for sub in range(2):
                ht = t + sub * eighth + rng.uniform(-0.005, 0.005)
                notes.append(_drum_note(HAT_CLOSED, max(0.0, ht), velocity=rng.randint(50, 100)))
    return notes


def fill(
    beats: int = 1,
    tempo: float = 120,
    seed: int = 0,
    start: float = 0.0,
) -> list[pretty_midi.Note]:
    """Short stumbling fill using toms and snare."""
    rng = SeededRng(seed)
    beat_dur = 60.0 / tempo
    sixteenth = beat_dur / 4.0
    total_sixteenths = beats * 4
    fill_instruments = [SNARE, FLOOR_TOM, RACK_TOM]
    notes = []

    for i in range(total_sixteenths):
        if rng.random() < 0.3:
            continue
        t = start + i * sixteenth + rng.uniform(-0.008, 0.008)
        pitch = fill_instruments[rng.randint(0, len(fill_instruments) - 1)]
        vel = rng.randint(70, 110)
        notes.append(_drum_note(pitch, max(0.0, t), velocity=vel))
    return notes
