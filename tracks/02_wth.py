#!/usr/bin/env python
"""Track 02: wth — Confusion deepens. Same key as wtf but tempo jumps, 7/8 time.
A 2-bar melody loop repeats and mutates until unrecognizable."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


import pretty_midi
from lib.composer import Composer
from lib.constants import BASS_FINGER, LEAD_SQUARE, GUITAR_CLEAN, DRUM_CHANNEL
from lib.drums import driving_emo, blast, half_time
from lib.harmony import chord
from lib.melody import stutter, contour, broken_trail
from lib.bass import counter_melody
from lib.humanize import humanize_timing, humanize_velocity, strum, SeededRng
from lib.directives import loop_that_breaks
from lib.cli import parse_track_args
from lib.constants import CRASH


def generate(seed=None):
    c = Composer(2, "wth", key="Em", tempo=152, time_sig=(7, 8), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    eighth = beat / 2.0
    bar = c.bar_duration  # 7/8 bar = 7 * eighth

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_FINGER)
    chords_inst = c.add_instrument("Chords", program=GUITAR_CLEAN)
    melody_inst = c.add_instrument("Melody", program=LEAD_SQUARE)

    # Progression: i - bII in 7/8
    chord_seq = [("E", "min"), ("F", "min")]

    # === Section 1: Loop That Breaks — 2-bar loop × 4 reps (~14s) ===
    # Build the base 2-bar melody loop
    base_melody = []
    # Start with stutter on E4, then evolve
    stut = stutter(pitch=64, count=4, note_duration=eighth * 0.8, gap=eighth * 0.2,
                   start=0.0, velocity=95)
    base_melody.extend(stut)
    # Add a descending phrase in second bar
    desc = contour("Em", "phrygian", direction="descending", num_notes=5,
                   octave=4, seed=c.seed, start_time=bar,
                   note_duration=eighth * 1.5, note_gap=eighth * 0.5, velocity=90)
    base_melody.extend(desc)

    loop_result = loop_that_breaks(base_melody, repetitions=4, seed=c.seed)
    for rep_notes in loop_result:
        melody_inst.notes.extend(rep_notes)

    # Drums and chords for loop section (8 bars of 7/8)
    drum_loop = driving_emo(bars=8, tempo=152, time_sig=(7, 8), seed=c.seed)
    drums_inst.notes.extend(drum_loop)

    for bar_idx in range(8):
        t = bar_idx * bar
        root, quality = chord_seq[bar_idx % 2]
        pitches = chord(root, quality, octave=2, voicing="open")
        chord_notes = [pretty_midi.Note(velocity=75 + rng.randint(-5, 5), pitch=p,
                       start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(chord_notes, direction="down", spread_ms=20))

    # Bass: simple root movement for loop section
    for bar_idx in range(8):
        t = bar_idx * bar
        root_pitch = 28 if bar_idx % 2 == 0 else 29  # E1 or F1
        bass_inst.notes.append(pretty_midi.Note(velocity=95, pitch=root_pitch,
                               start=t, end=t + bar * 0.7))

    # === Section 2: Bars 9-12 — Blast beat + stutter melody ===
    offset_s2 = 8 * bar
    blast_notes = blast(bars=4, tempo=152, time_sig=(7, 8), seed=c.seed + 1)
    for n in blast_notes:
        n.start += offset_s2
        n.end += offset_s2
    drums_inst.notes.extend(blast_notes)

    # Stutter melody during blast
    stut2 = stutter(pitch=64, count=16, note_duration=eighth * 0.5, gap=eighth * 0.3,
                    start=offset_s2, velocity=110)
    melody_inst.notes.extend(stut2)

    # Bass counter-melody with wide leaps
    bass_counter = counter_melody("Em", "phrygian", bars=4, tempo=152,
                                  time_sig=(7, 8), seed=c.seed + 1, velocity=100)
    for n in bass_counter:
        n.start += offset_s2
        n.end += offset_s2
    bass_inst.notes.extend(bass_counter)

    # Chords: power chords during blast
    for bar_idx in range(4):
        t = offset_s2 + bar_idx * bar
        root, _ = chord_seq[bar_idx % 2]
        pitches = chord(root, "power", octave=2)
        for p in pitches:
            chords_inst.notes.append(pretty_midi.Note(velocity=110, pitch=p,
                                     start=t, end=t + bar * 0.9))

    # === Section 3: Bars 13-15 — Half-time collapse + broken trail ===
    offset_s3 = 12 * bar
    ht_notes = half_time(bars=3, tempo=152, time_sig=(7, 8), seed=c.seed + 2)
    for n in ht_notes:
        n.start += offset_s3
        n.end += offset_s3
    drums_inst.notes.extend(ht_notes)

    trail_melody = contour("Em", "phrygian", direction="descending", num_notes=10,
                           octave=4, seed=c.seed + 3, start_time=offset_s3,
                           note_duration=eighth * 2, note_gap=eighth, velocity=70)
    trail_melody = broken_trail(trail_melody, decay_point=4)
    melody_inst.notes.extend(trail_melody)

    # Sparse bass
    bass_inst.notes.append(pretty_midi.Note(velocity=60, pitch=28,
                           start=offset_s3, end=offset_s3 + bar * 2))

    # Sparse chords
    pitches = chord("E", "sus2", octave=2, voicing="open")
    for p in pitches:
        chords_inst.notes.append(pretty_midi.Note(velocity=50, pitch=p,
                                 start=offset_s3, end=offset_s3 + bar * 2))

    # === Final: silence + one crash ===
    crash_time = min(offset_s3 + 3 * bar, c.duration - 0.5)
    if crash_time > 0 and crash_time < c.duration:
        drums_inst.notes.append(pretty_midi.Note(velocity=120, pitch=CRASH,
                                start=crash_time, end=crash_time + 0.4))

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
