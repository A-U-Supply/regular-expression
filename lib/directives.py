"""Special structural directives for the album.

These return plans (bar boundaries, note lists) that track scripts use
to structure their compositions. They don't modify Composer state directly.
"""

import pretty_midi
from lib.humanize import SeededRng


def collapse_plan(
    total_bars: int,
    collapse_bar: int,
    re_entry_bar: int,
) -> dict:
    """Plan for The Collapse directive."""
    return {
        "before": (0, collapse_bar),
        "solo": (collapse_bar, re_entry_bar),
        "after": (re_entry_bar, total_bars),
    }


def loop_that_breaks(
    base_notes: list[pretty_midi.Note],
    repetitions: int = 4,
    seed: int = 0,
) -> list[list[pretty_midi.Note]]:
    """Repeat a passage with cumulative mutations."""
    rng = SeededRng(seed)
    loop_duration = max(n.end for n in base_notes) - min(n.start for n in base_notes)
    result = []

    for rep in range(repetitions):
        time_offset = rep * loop_duration
        rep_notes = []
        for n in base_notes:
            pitch = n.pitch
            start = n.start + time_offset
            end = n.end + time_offset
            vel = n.velocity

            if rep > 0:
                for _ in range(rep):
                    mutation = rng.randint(0, 2)
                    if mutation == 0 and rng.random() < 0.3 * rep:
                        continue
                    elif mutation == 1:
                        pitch += rng.randint(-2, 2)
                    elif mutation == 2:
                        start += rng.uniform(-0.05, 0.05) * rep

            rep_notes.append(pretty_midi.Note(
                velocity=max(1, min(127, vel)),
                pitch=max(0, min(127, pitch)),
                start=max(0.0, start),
                end=max(start + 0.01, end),
            ))
        result.append(rep_notes)
    return result


def two_songs_stitched_plan(
    total_bars: int,
    split_bar: int,
    transition_bars: int = 1,
) -> dict:
    """Plan for Two Songs Stitched directive."""
    return {
        "song_a": (0, split_bar),
        "transition": (split_bar, split_bar + transition_bars),
        "song_b": (split_bar + transition_bars, total_bars),
    }


def countdown_plan(
    tempo: float,
    time_sig: tuple[int, int],
    section_bars: list[int] | None = None,
) -> dict:
    """Plan for The Countdown directive."""
    if section_bars is None:
        section_bars = [8, 4, 2, 1]
    boundaries = []
    current = 0
    for bars in section_bars:
        boundaries.append((current, current + bars))
        current += bars
    return {
        "section_bars": section_bars,
        "bar_boundaries": boundaries,
    }


def unison_collapse(
    target_pitch: int,
    num_instruments: int,
    start: float,
    duration: float,
    velocity: int = 80,
) -> list[pretty_midi.Note]:
    """All instruments converge on one note/octave."""
    notes = []
    octave_offsets = [0, 0, 12, -12]
    for i in range(num_instruments):
        offset = octave_offsets[i % len(octave_offsets)]
        pitch = max(0, min(127, target_pitch + offset))
        notes.append(pretty_midi.Note(
            velocity=velocity, pitch=pitch, start=start, end=start + duration,
        ))
    return notes


def reverse_structure_plan(
    total_bars: int,
    num_instruments: int,
) -> list[dict]:
    """Plan for Reverse Structure directive."""
    bars_per_section = max(1, total_bars // num_instruments)
    plan = []
    current_bar = 0
    for i in range(num_instruments):
        remaining = num_instruments - i
        end_bar = min(current_bar + bars_per_section, total_bars)
        if i == num_instruments - 1:
            end_bar = total_bars
        plan.append({
            "bars": (current_bar, end_bar),
            "num_instruments": remaining,
        })
        current_bar = end_bar
    return plan


def rhythmic_displacement(
    notes: list[pretty_midi.Note],
    offset_eighths: int = 1,
    tempo: float = 120,
) -> list[pretty_midi.Note]:
    """Shift all notes by a number of eighth notes. Feels persistently wrong."""
    eighth_dur = 60.0 / tempo / 2.0
    offset = offset_eighths * eighth_dur
    return [
        pretty_midi.Note(
            velocity=n.velocity,
            pitch=n.pitch,
            start=max(0.0, n.start + offset),
            end=max(0.01, n.end + offset),
        )
        for n in notes
    ]


def drone(
    pitch: int,
    duration: float = 30.0,
    velocity: int = 45,
) -> pretty_midi.Note:
    """A single sustained low note for the entire track."""
    return pretty_midi.Note(velocity=velocity, pitch=pitch, start=0.0, end=duration)
