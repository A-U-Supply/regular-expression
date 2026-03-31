#!/usr/bin/env python
"""Track 08: dumbass — Angular, ugly 5/4 stumble. A 2-bar loop that mutates and
degrades across repetitions. Then anxious, then blast, then silence."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_PICK, LEAD_SQUARE, GUITAR_OVERDRIVE,
                           DRUM_CHANNEL, CRASH, KICK, SNARE)
from lib.drums import driving_emo, blast, no_snare
from lib.harmony import chord
from lib.melody import contour, stutter
from lib.bass import driving_eighths, locked_bass
from lib.humanize import strum, SeededRng
from lib.directives import loop_that_breaks
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(8, "dumbass", key="F#m", tempo=144, time_sig=(5, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration  # 5 beats at 144bpm

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_PICK)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=LEAD_SQUARE)

    # F# Phrygian: F# G A B C# D E
    chord_seq = [("F#", "min"), ("G", "min"), ("C#", "min"), ("F#", "min"), ("B", "min")]

    # === Build the base 2-bar loop ===
    loop_dur = 2 * bar

    # Base drum loop notes (2 bars of 5/4)
    base_drums = driving_emo(bars=2, tempo=144, time_sig=(5, 4), seed=c.seed)

    # Base melody for the loop — angular, short
    base_mel = contour("F#m", "phrygian", direction="ascending", num_notes=8,
                       octave=4, seed=c.seed, start_time=0.0,
                       note_duration=beat * 0.5, note_gap=beat * 0.15, velocity=100)

    # Base bass loop
    base_kick_times = [b * beat for i in range(2) for b in [i * 5 * beat, i * 5 * beat + 2 * beat]]
    base_kick_times = [i * 5 * beat + b * beat for i in range(2) for b in [0, 2, 4]]

    # === Section 1: Loop × 4 mutating ===
    loop_notes = loop_that_breaks(base_mel, repetitions=4, seed=c.seed)

    for rep_idx, rep_notes in enumerate(loop_notes):
        time_offset = rep_idx * loop_dur
        # Drums
        drum_rep = driving_emo(bars=2, tempo=144, time_sig=(5, 4), seed=c.seed + rep_idx)
        for n in drum_rep:
            n.start += time_offset
            n.end += time_offset
            n.velocity = max(1, min(127, n.velocity + rep_idx * 5))
        drums_inst.notes.extend(drum_rep)

        # Melody mutations
        for n in rep_notes:
            melody_inst.notes.append(pretty_midi.Note(
                velocity=n.velocity,
                pitch=max(0, min(127, n.pitch)),
                start=n.start + time_offset,
                end=n.end + time_offset,
            ))

        # Chords each rep
        for ci in range(2):
            t = time_offset + ci * bar
            root, q = chord_seq[ci % len(chord_seq)]
            pitches = chord(root, q, octave=2, voicing="closed")
            cn = [pretty_midi.Note(velocity=80 + rep_idx * 5, pitch=p,
                                   start=t, end=t + bar * 0.8) for p in pitches]
            chords_inst.notes.extend(strum(cn, direction="down", spread_ms=15))

        # Bass
        kick_t = [time_offset + i * 5 * beat + b * beat for i in range(2) for b in [0, 2, 4]]
        bass_rep = locked_bass(kick_t, root=30, fifth=37, bars=2, tempo=144,
                               seed=c.seed + rep_idx, velocity=95 + rep_idx * 5)
        bass_inst.notes.extend(bass_rep)

    # === Section 2: 4 bars no-snare (anxious) ===
    s2 = 4 * loop_dur
    ns = no_snare(bars=4, tempo=144, time_sig=(5, 4), seed=c.seed + 4)
    for n in ns:
        n.start += s2
        n.end += s2
    drums_inst.notes.extend(ns)

    # Stutter melody — single note obsessive
    stut = stutter(pitch=66, count=16, note_duration=beat * 0.25, gap=beat * 0.08,
                   start=s2, velocity=90)
    melody_inst.notes.extend(stut)

    for i in range(4):
        t = s2 + i * bar
        bass_inst.notes.append(pretty_midi.Note(velocity=80, pitch=30,
                               start=t, end=t + bar * 0.6))

    # === Section 3: 2 bars blast ===
    s3 = s2 + 4 * bar
    bl = blast(bars=2, tempo=144, time_sig=(5, 4), seed=c.seed + 5)
    for n in bl:
        n.start += s3
        n.end += s3
        n.velocity = min(127, n.velocity + 15)
    drums_inst.notes.extend(bl)

    for i in range(2):
        t = s3 + i * bar
        pitches = chord("F#", "min", octave=2, voicing="closed")
        cn = [pretty_midi.Note(velocity=120, pitch=p, start=t, end=t + bar * 0.9) for p in pitches]
        chords_inst.notes.extend(cn)
        bass_inst.notes.append(pretty_midi.Note(velocity=120, pitch=30,
                               start=t, end=t + beat))

    # === Section 4: Silence (notes end naturally) ===
    # No notes added — the track ends in silence

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
