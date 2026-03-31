#!/usr/bin/env python
"""Track 09: horrible — Self-lacerating. D1 drone (26) sustains throughout.
Builds from nothing, drops back to drone + one note, then full re-entry."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_FINGER, GUITAR_DISTORTION, GUITAR_OVERDRIVE,
                           DRUM_CHANNEL, CRASH, KICK)
from lib.drums import driving_emo, half_time
from lib.harmony import chord, cluster
from lib.melody import contour, phrase
from lib.bass import locked_bass, driving_eighths
from lib.humanize import strum, humanize_velocity, SeededRng
from lib.directives import drone
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(9, "horrible", key="Dm", tempo=122, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_FINGER)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)
    drone_inst = c.add_instrument("Drone", program=BASS_FINGER)

    # D1 drone (MIDI 26) — D is one below E1=28, so D1 = 26
    drone_note = drone(pitch=26, duration=c.duration, velocity=42)
    drone_inst.notes.append(drone_note)

    # Dm natural minor chords
    chord_seq = [("D", "min"), ("F", "min"), ("C", "min"), ("A", "min")]

    # === Section 1: Bars 1-2 — Drone alone ===
    # Nothing added — drone plays solo

    # === Section 2: Bars 3-6 — Drums + bass enter ===
    s2 = 2 * bar
    de_s2 = half_time(bars=4, tempo=122, time_sig=(4, 4), seed=c.seed)
    for n in de_s2:
        n.start += s2
        n.end += s2
    drums_inst.notes.extend(de_s2)

    kick_times = [s2 + i * bar + b * beat for i in range(4) for b in [0, 2]]
    bass_s2 = locked_bass(kick_times, root=38, fifth=45, bars=4, tempo=122,
                          seed=c.seed, velocity=85)
    bass_inst.notes.extend(bass_s2)

    # === Section 3: Bars 7-10 — Chords + melody enter with clusters ===
    s3 = 6 * bar
    de_s3 = driving_emo(bars=4, tempo=122, time_sig=(4, 4), seed=c.seed + 1)
    for n in de_s3:
        n.start += s3
        n.end += s3
    drums_inst.notes.extend(de_s3)

    kick_times_s3 = [s3 + i * bar + b * beat for i in range(4) for b in [0, 2]]
    bass_s3 = locked_bass(kick_times_s3, root=38, fifth=45, bars=4, tempo=122,
                          seed=c.seed + 1, velocity=100)
    bass_inst.notes.extend(bass_s3)

    for i in range(4):
        t = s3 + i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=90 + rng.randint(-5, 5), pitch=p,
                               start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=25))

    mel_s3 = contour("Dm", "natural_minor", direction="descending", num_notes=14,
                     octave=4, seed=c.seed + 1, start_time=s3,
                     note_duration=beat * 0.6, note_gap=beat * 0.2, velocity=95)
    melody_inst.notes.extend(mel_s3)

    # Cluster stab at bar 9 (2 bars into s3)
    cluster_pitches = cluster(center_pitch=62, width=2)  # D4 cluster
    for cp in cluster_pitches:
        t_cl = s3 + 2 * bar
        chords_inst.notes.append(pretty_midi.Note(velocity=100, pitch=cp,
                                  start=t_cl, end=t_cl + beat * 0.3))

    # === Section 4: Bars 11-12 — Drop to drone + one note ===
    s4 = 10 * bar
    # Single melody note sustained
    melody_inst.notes.append(pretty_midi.Note(velocity=60, pitch=62,  # D4
                              start=s4, end=s4 + 2 * bar))

    # === Section 5: Bars 13-14 — Full re-entry ===
    s5 = 12 * bar
    if s5 < c.duration:
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=CRASH,
                                start=s5, end=s5 + 0.4))
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=KICK,
                                start=s5, end=s5 + 0.1))

        de_s5 = driving_emo(bars=2, tempo=122, time_sig=(4, 4), seed=c.seed + 2)
        for n in de_s5:
            n.start += s5
            n.end += s5
            n.velocity = min(127, n.velocity + 20)
            if n.start < c.duration:
                drums_inst.notes.append(n)

        pitches = chord("D", "min", octave=2, voicing="open")
        for p in pitches:
            chords_inst.notes.append(pretty_midi.Note(velocity=115, pitch=p,
                                      start=s5, end=min(c.duration, s5 + bar)))

        bass_inst.notes.append(pretty_midi.Note(velocity=115, pitch=38,
                               start=s5, end=min(c.duration, s5 + bar)))

        mel_s5 = contour("Dm", "natural_minor", direction="ascending", num_notes=8,
                         octave=4, seed=c.seed + 3, start_time=s5,
                         note_duration=beat * 0.5, note_gap=beat * 0.15, velocity=110)
        for n in mel_s5:
            if n.start < c.duration:
                melody_inst.notes.append(n)

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
