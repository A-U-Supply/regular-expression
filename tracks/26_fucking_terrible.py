#!/usr/bin/env python
"""Track 26: fucking terrible — Maximum aggression. F#m Phrygian, 160bpm (tied fastest).
Countdown + blast beats. The Countdown directive."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_PICK, LEAD_SQUARE, GUITAR_OVERDRIVE,
                           DRUM_CHANNEL, CRASH, KICK)
from lib.drums import blast, driving_emo, no_snare
from lib.harmony import chord, cluster
from lib.melody import contour, stutter, spike
from lib.bass import locked_bass, driving_eighths
from lib.humanize import strum, humanize_velocity, SeededRng
from lib.directives import countdown_plan
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(26, "fucking_terrible", key="F#m", tempo=160, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_PICK)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=LEAD_SQUARE)

    # F# Phrygian: F# G A B C# D E
    chord_seq = [("F#", "min"), ("G", "min"), ("C#", "min"), ("F#", "min")]
    fs_root = 30  # F#1

    # Countdown: 6→3→2→1 bars
    plan = countdown_plan(tempo=160, time_sig=(4, 4), section_bars=[6, 3, 2, 1])

    # === Section 1: 6 bars — Full blast from the start ===
    s1 = 0.0
    bl_s1 = blast(bars=4, tempo=160, time_sig=(4, 4), seed=c.seed)
    for n in bl_s1:
        n.velocity = min(127, n.velocity + 15)
    drums_inst.notes.extend(bl_s1)

    de_s1 = driving_emo(bars=2, tempo=160, time_sig=(4, 4), seed=c.seed + 10)
    for n in de_s1:
        n.start += 4 * bar
        n.end += 4 * bar
        n.velocity = min(127, n.velocity + 20)
    drums_inst.notes.extend(de_s1)

    kick_times = [i * bar + b * beat for i in range(6) for b in [0, 2]]
    bass_s1 = locked_bass(kick_times, root=fs_root, fifth=37, bars=6,
                          tempo=160, seed=c.seed, velocity=115)
    bass_inst.notes.extend(bass_s1)

    for i in range(6):
        t = i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="closed")
        cn = [pretty_midi.Note(velocity=105 + rng.randint(-5, 5), pitch=p,
                               start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=10))

    mel_s1 = contour("F#m", "phrygian", direction="ascending", num_notes=20,
                     octave=4, seed=c.seed, start_time=s1,
                     note_duration=beat * 0.3, note_gap=beat * 0.07, velocity=110)
    melody_inst.notes.extend(mel_s1)

    # === Section 2: 3 bars — Louder, blast ===
    s2 = 6 * bar
    bl_s2 = blast(bars=3, tempo=160, time_sig=(4, 4), seed=c.seed + 1)
    for n in bl_s2:
        n.start += s2
        n.end += s2
        n.velocity = min(127, n.velocity + 18)
    drums_inst.notes.extend(bl_s2)

    de_bass_s2 = driving_eighths(root=fs_root, bars=3, tempo=160, time_sig=(4, 4), velocity=122)
    for n in de_bass_s2:
        n.start += s2
        n.end += s2
    bass_inst.notes.extend(de_bass_s2)

    for i in range(3):
        t = s2 + i * bar
        pitches = chord("F#", "min", octave=2, voicing="closed")
        cn = [pretty_midi.Note(velocity=118, pitch=p, start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=8))

    mel_s2 = contour("F#m", "phrygian", direction="descending", num_notes=14,
                     octave=5, seed=c.seed + 1, start_time=s2,
                     note_duration=beat * 0.28, note_gap=beat * 0.06, velocity=118)
    melody_inst.notes.extend(mel_s2)

    # Cluster stab
    cluster_pitches = cluster(center_pitch=66, width=2)
    for cp in cluster_pitches:
        chords_inst.notes.append(pretty_midi.Note(velocity=120, pitch=cp,
                                  start=s2 + bar, end=s2 + bar + beat * 0.3))

    # === Section 3: 2 bars — Maximum intensity ===
    s3 = 9 * bar
    bl_s3 = blast(bars=2, tempo=160, time_sig=(4, 4), seed=c.seed + 2)
    for n in bl_s3:
        n.start += s3
        n.end += s3
        n.velocity = 127
    drums_inst.notes.extend(bl_s3)

    de_bass_s3 = driving_eighths(root=fs_root, bars=2, tempo=160, time_sig=(4, 4), velocity=127)
    for n in de_bass_s3:
        n.start += s3
        n.end += s3
    bass_inst.notes.extend(de_bass_s3)

    stut = stutter(pitch=78, count=16, note_duration=beat * 0.12, gap=0.01,
                   start=s3, velocity=127)
    melody_inst.notes.extend(stut)

    # === Section 4: 1 bar — Final crash then silence ===
    s4 = 11 * bar
    if s4 < c.duration:
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=CRASH,
                                start=s4, end=s4 + 0.4))
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=KICK,
                                start=s4, end=s4 + 0.1))
        bass_inst.notes.append(pretty_midi.Note(velocity=127, pitch=fs_root,
                               start=s4, end=min(c.duration, s4 + beat)))
        melody_inst.notes.append(pretty_midi.Note(velocity=127, pitch=66,  # F#4
                                  start=s4, end=min(c.duration, s4 + beat * 0.5)))

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
