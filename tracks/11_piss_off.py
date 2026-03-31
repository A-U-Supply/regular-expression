#!/usr/bin/env python
"""Track 11: piss off — Conjugation trilogy base. Countdown sections (8→4→2→1 bars)
getting shorter and more intense. Core melodic material used in 12 and 13."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_PICK, GUITAR_DISTORTION, GUITAR_OVERDRIVE,
                           DRUM_CHANNEL, CRASH, KICK)
from lib.drums import driving_emo, blast, no_snare
from lib.harmony import chord
from lib.melody import contour, stutter
from lib.bass import locked_bass, driving_eighths
from lib.humanize import strum, humanize_velocity, SeededRng
from lib.directives import countdown_plan
from lib.cli import parse_track_args


# === Shared melodic material for the conjugation trilogy (tracks 11-13) ===
# Em natural minor: E F# G A B C D
TRILOGY_MELODY_PITCHES = [64, 62, 60, 57, 59, 55, 57, 59, 60, 62, 64, 66]
# (E4, D4, C4, A3, B3, G3, A3, B3, C4, D4, E4, F#4)
TRILOGY_CHORD_SEQ = [("E", "min"), ("G", "min"), ("D", "min"), ("A", "min")]
TRILOGY_ROOT = 28  # E1


def generate(seed=None):
    c = Composer(11, "piss_off", key="Em", tempo=132, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_PICK)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    plan = countdown_plan(tempo=132, time_sig=(4, 4), section_bars=[8, 4, 2, 1])
    # Total = 15 bars but we have ~14 at 132bpm in 30s

    # === Section 1: 8 bars — moderate, driving ===
    s1_start, s1_end = 0, 8 * bar
    de_s1 = driving_emo(bars=8, tempo=132, time_sig=(4, 4), seed=c.seed)
    drums_inst.notes.extend(de_s1)

    kick_times_s1 = [i * bar + b * beat for i in range(8) for b in [0, 2]]
    bass_s1 = locked_bass(kick_times_s1, root=TRILOGY_ROOT, fifth=35, bars=8,
                          tempo=132, seed=c.seed, velocity=95)
    bass_inst.notes.extend(bass_s1)

    for i in range(8):
        t = i * bar
        root, q = TRILOGY_CHORD_SEQ[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=85 + rng.randint(-5, 5), pitch=p,
                               start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=25))

    # Melody from shared pitches
    mel_t = 0.0
    for pitch in TRILOGY_MELODY_PITCHES:
        melody_inst.notes.append(pretty_midi.Note(velocity=90, pitch=pitch,
                                  start=mel_t, end=mel_t + beat * 0.8))
        mel_t += beat

    # === Section 2: 4 bars — louder, no-snare anxiety ===
    s2 = 8 * bar
    ns = no_snare(bars=4, tempo=132, time_sig=(4, 4), seed=c.seed + 1)
    for n in ns:
        n.start += s2
        n.end += s2
        n.velocity = min(127, n.velocity + 10)
    drums_inst.notes.extend(ns)

    kick_times_s2 = [s2 + i * bar + b * beat for i in range(4) for b in [0, 2]]
    bass_s2 = locked_bass(kick_times_s2, root=TRILOGY_ROOT, fifth=35, bars=4,
                          tempo=132, seed=c.seed + 1, velocity=110)
    bass_inst.notes.extend(bass_s2)

    for i in range(4):
        t = s2 + i * bar
        root, q = TRILOGY_CHORD_SEQ[i % 4]
        pitches = chord(root, q, octave=2, voicing="closed")
        cn = [pretty_midi.Note(velocity=100, pitch=p, start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=15))

    # Melody repeated faster
    mel_t2 = s2
    for pitch in TRILOGY_MELODY_PITCHES:
        melody_inst.notes.append(pretty_midi.Note(velocity=100, pitch=pitch + 12,  # octave up
                                  start=mel_t2, end=mel_t2 + beat * 0.6))
        mel_t2 += beat * 0.75

    # === Section 3: 2 bars — blast beat ===
    s3 = 12 * bar
    bl = blast(bars=2, tempo=132, time_sig=(4, 4), seed=c.seed + 2)
    for n in bl:
        n.start += s3
        n.end += s3
        n.velocity = min(127, n.velocity + 15)
    drums_inst.notes.extend(bl)

    kick_times_s3 = [s3 + i * bar + b * beat for i in range(2) for b in [0, 2]]
    bass_s3 = locked_bass(kick_times_s3, root=TRILOGY_ROOT, fifth=35, bars=2,
                          tempo=132, seed=c.seed + 2, velocity=120)
    bass_inst.notes.extend(bass_s3)

    pitches = chord("E", "min", octave=2, voicing="closed")
    for p in pitches:
        chords_inst.notes.append(pretty_midi.Note(velocity=115, pitch=p,
                                  start=s3, end=s3 + 2 * bar))

    stut = stutter(pitch=64, count=8, note_duration=beat * 0.25, gap=0.02,
                   start=s3, velocity=110)
    melody_inst.notes.extend(stut)

    # === Section 4: 1 bar — single crash + one note ===
    s4 = 14 * bar
    if s4 < c.duration:
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=CRASH,
                                start=s4, end=s4 + 0.4))
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=KICK,
                                start=s4, end=s4 + 0.1))
        melody_inst.notes.append(pretty_midi.Note(velocity=127, pitch=64,
                                  start=s4, end=min(c.duration, s4 + beat * 2)))
        bass_inst.notes.append(pretty_midi.Note(velocity=127, pitch=TRILOGY_ROOT,
                               start=s4, end=min(c.duration, s4 + bar)))

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
