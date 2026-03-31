#!/usr/bin/env python
"""Track 21: fuck terrible — Relentless. F#m Phrygian, 158bpm. Blast-heavy.
Countdown 6→3→1 bars. Accelerating intensity."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_PICK, LEAD_SQUARE, GUITAR_OVERDRIVE,
                           DRUM_CHANNEL, CRASH, KICK)
from lib.drums import blast, driving_emo, no_snare
from lib.harmony import chord
from lib.melody import contour, stutter, spike
from lib.bass import locked_bass, driving_eighths
from lib.humanize import strum, humanize_velocity, SeededRng
from lib.directives import countdown_plan
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(21, "fuck_terrible", key="F#m", tempo=158, time_sig=(4, 4), seed=seed)
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

    # Countdown: 6→3→1 bars (fits 30s at 158bpm)
    plan = countdown_plan(tempo=158, time_sig=(4, 4), section_bars=[6, 3, 1])

    # === Section 1: 6 bars — Driving fury ===
    s1 = 0.0
    de = driving_emo(bars=6, tempo=158, time_sig=(4, 4), seed=c.seed)
    for n in de:
        n.velocity = min(127, n.velocity + 15)
    drums_inst.notes.extend(de)

    kick_times = [i * bar + b * beat for i in range(6) for b in [0, 2]]
    bass_s1 = locked_bass(kick_times, root=fs_root, fifth=37, bars=6,
                          tempo=158, seed=c.seed, velocity=110)
    bass_inst.notes.extend(bass_s1)

    for i in range(6):
        t = i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="closed")
        cn = [pretty_midi.Note(velocity=100 + rng.randint(-5, 5), pitch=p,
                               start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=12))

    mel_s1 = contour("F#m", "phrygian", direction="ascending", num_notes=18,
                     octave=4, seed=c.seed, start_time=s1,
                     note_duration=beat * 0.35, note_gap=beat * 0.08, velocity=105)
    melody_inst.notes.extend(mel_s1)

    # === Section 2: 3 bars — Blast + louder ===
    s2 = 6 * bar
    bl_s2 = blast(bars=3, tempo=158, time_sig=(4, 4), seed=c.seed + 1)
    for n in bl_s2:
        n.start += s2
        n.end += s2
        n.velocity = min(127, n.velocity + 15)
    drums_inst.notes.extend(bl_s2)

    # Driving eighths bass
    de_bass = driving_eighths(root=fs_root, bars=3, tempo=158, time_sig=(4, 4), velocity=120)
    for n in de_bass:
        n.start += s2
        n.end += s2
    bass_inst.notes.extend(de_bass)

    for i in range(3):
        t = s2 + i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="closed")
        cn = [pretty_midi.Note(velocity=115, pitch=p, start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=10))

    # Melody: stutter + spike
    spike_notes = spike(base_pitch=66, interval="P5", start=s2, velocity=120)
    melody_inst.notes.extend(spike_notes)

    mel_s2 = contour("F#m", "phrygian", direction="descending", num_notes=12,
                     octave=5, seed=c.seed + 1, start_time=s2 + beat,
                     note_duration=beat * 0.3, note_gap=beat * 0.05, velocity=115)
    melody_inst.notes.extend(mel_s2)

    # === Section 3: 1 bar — Maximum hit ===
    s3 = 9 * bar
    if s3 < c.duration:
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=CRASH,
                                start=s3, end=s3 + 0.4))
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=KICK,
                                start=s3, end=s3 + 0.1))

        # Continue blast through end
        bl_s3 = blast(bars=4, tempo=158, time_sig=(4, 4), seed=c.seed + 2)
        for n in bl_s3:
            n.start += s3
            n.end += s3
            n.velocity = 127
            if n.start < c.duration:
                drums_inst.notes.append(n)

        pitches = chord("F#", "min", octave=2, voicing="closed")
        for p in pitches:
            chords_inst.notes.append(pretty_midi.Note(velocity=127, pitch=p,
                                      start=s3, end=min(c.duration, s3 + bar)))

        de_bass_s3 = driving_eighths(root=fs_root, bars=4, tempo=158, time_sig=(4, 4), velocity=127)
        for n in de_bass_s3:
            n.start += s3
            n.end += s3
            if n.start < c.duration:
                bass_inst.notes.append(n)

        # High pitched scream melody
        stut = stutter(pitch=78, count=16, note_duration=beat * 0.15, gap=0.01,
                       start=s3, velocity=127)
        for n in stut:
            if n.start < c.duration:
                melody_inst.notes.append(n)

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
