#!/usr/bin/env python
"""Track 17: what the fuck — Twin A. Furious. Bm Phrygian, 150bpm. Countdown.
Defines the shared twin melody that track 18 reuses in slow Dorian form."""

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


# === Shared twin melody (track 18 imports this) ===
# Bm Phrygian: B C D E F# G A
# Furious, jagged contour
TWIN_MELODY_PITCHES = [59, 60, 62, 64, 66, 64, 62, 60, 59, 57, 59, 62, 64, 60, 59]
# B3, C4, D4, E4, F#4, E4, D4, C4, B3, A3, B3, D4, E4, C4, B3


def generate(seed=None):
    c = Composer(17, "what_the_fuck", key="Bm", tempo=150, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_PICK)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    chord_seq = [("B", "min"), ("C", "min"), ("F#", "min"), ("B", "min")]
    bm_root = 35  # B1

    # Countdown: sections 6→4→2→1 bars
    plan = countdown_plan(tempo=150, time_sig=(4, 4), section_bars=[6, 4, 2, 1])

    # === Section 1: 6 bars — Full fury ===
    s1 = 0.0
    de = driving_emo(bars=6, tempo=150, time_sig=(4, 4), seed=c.seed)
    for n in de:
        n.velocity = min(127, n.velocity + 10)
    drums_inst.notes.extend(de)

    kick_times = [i * bar + b * beat for i in range(6) for b in [0, 2]]
    bass_s1 = locked_bass(kick_times, root=bm_root, fifth=42, bars=6,
                          tempo=150, seed=c.seed, velocity=110)
    bass_inst.notes.extend(bass_s1)

    for i in range(6):
        t = i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="closed")
        cn = [pretty_midi.Note(velocity=100 + rng.randint(-5, 5), pitch=p,
                               start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=15))

    # Twin melody — full speed
    mel_t = 0.0
    for pitch in TWIN_MELODY_PITCHES:
        melody_inst.notes.append(pretty_midi.Note(velocity=105, pitch=pitch,
                                  start=mel_t, end=mel_t + beat * 0.6))
        mel_t += beat * 0.75

    # === Section 2: 4 bars — No-snare, intensifying ===
    s2 = 6 * bar
    ns = no_snare(bars=4, tempo=150, time_sig=(4, 4), seed=c.seed + 1)
    for n in ns:
        n.start += s2
        n.end += s2
        n.velocity = min(127, n.velocity + 10)
    drums_inst.notes.extend(ns)

    kick_times_s2 = [s2 + i * bar + b * beat for i in range(4) for b in [0, 2]]
    bass_s2 = locked_bass(kick_times_s2, root=bm_root, fifth=42, bars=4,
                          tempo=150, seed=c.seed + 1, velocity=115)
    bass_inst.notes.extend(bass_s2)

    for i in range(4):
        t = s2 + i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="closed")
        cn = [pretty_midi.Note(velocity=105, pitch=p, start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=12))

    # Melody repeats at higher octave
    mel_t2 = s2
    for pitch in TWIN_MELODY_PITCHES:
        melody_inst.notes.append(pretty_midi.Note(velocity=110, pitch=min(127, pitch + 12),
                                  start=mel_t2, end=mel_t2 + beat * 0.5))
        mel_t2 += beat * 0.62

    # === Section 3: 2 bars — Blast ===
    s3 = 10 * bar
    bl = blast(bars=2, tempo=150, time_sig=(4, 4), seed=c.seed + 2)
    for n in bl:
        n.start += s3
        n.end += s3
        n.velocity = min(127, n.velocity + 20)
    drums_inst.notes.extend(bl)

    kick_times_s3 = [s3 + b * beat for b in [0, 2]]
    bass_s3 = locked_bass(kick_times_s3, root=bm_root, fifth=42, bars=2,
                          tempo=150, seed=c.seed + 2, velocity=125)
    for n in bass_s3:
        if n.start < c.duration:
            bass_inst.notes.append(n)

    pitches = chord("B", "min", octave=2, voicing="closed")
    for p in pitches:
        chords_inst.notes.append(pretty_midi.Note(velocity=120, pitch=p,
                                  start=s3, end=min(c.duration, s3 + 2 * bar)))

    stut = stutter(pitch=59, count=10, note_duration=beat * 0.2, gap=0.02,
                   start=s3, velocity=120)
    melody_inst.notes.extend(stut)

    # === Section 4: 1 bar — Final crash ===
    s4 = 12 * bar
    if s4 < c.duration:
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=CRASH,
                                start=s4, end=s4 + 0.4))
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=KICK,
                                start=s4, end=s4 + 0.1))
        bass_inst.notes.append(pretty_midi.Note(velocity=127, pitch=bm_root,
                               start=s4, end=min(c.duration, s4 + beat * 2)))
        melody_inst.notes.append(pretty_midi.Note(velocity=127, pitch=59,  # B3
                                  start=s4, end=min(c.duration, s4 + beat)))

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
