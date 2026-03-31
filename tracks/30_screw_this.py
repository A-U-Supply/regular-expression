#!/usr/bin/env python
"""Track 30: screw this — Driving, direct. Em natural minor, 138bpm.
Chords displaced — they feel slightly wrong against the rhythm. Rhythmic Displacement (chords)."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_PICK, GUITAR_DISTORTION, GUITAR_OVERDRIVE,
                           DRUM_CHANNEL, CRASH, KICK)
from lib.drums import driving_emo, blast
from lib.harmony import chord
from lib.melody import contour, stutter, spike
from lib.bass import locked_bass, driving_eighths
from lib.humanize import strum, humanize_velocity, SeededRng
from lib.directives import rhythmic_displacement
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(30, "screw_this", key="Em", tempo=138, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_PICK)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    # Em natural minor
    chord_seq = [("E", "min"), ("G", "min"), ("D", "min"), ("A", "min")]
    em_root = 28  # E1

    total_bars = c.bars

    # === Full band, all bars ===
    de = driving_emo(bars=total_bars, tempo=138, time_sig=(4, 4), seed=c.seed)
    drums_inst.notes.extend(de)

    kick_times = [i * bar + b * beat for i in range(total_bars) for b in [0, 2]]
    bass_notes = locked_bass(kick_times, root=em_root, fifth=35, bars=total_bars,
                             tempo=138, seed=c.seed, velocity=105)
    bass_inst.notes.extend(bass_notes)

    # Build chords then displace them
    raw_chords = []
    for i in range(total_bars):
        t = i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        for p in pitches:
            raw_chords.append(pretty_midi.Note(velocity=90 + rng.randint(-5, 5), pitch=p,
                                               start=t, end=t + bar * 0.85))

    # Displace chords by 1.5 eighth notes
    displaced_chords = rhythmic_displacement(raw_chords, offset_eighths=3, tempo=138)
    # Filter to duration
    for n in displaced_chords:
        if n.start < c.duration:
            chords_inst.notes.append(n)

    # Melody: normal, 2 sections
    half = total_bars // 2
    mel_s1 = contour("Em", "natural_minor", direction="descending", num_notes=half * 3,
                     octave=4, seed=c.seed, start_time=0.0,
                     note_duration=beat * 0.5, note_gap=beat * 0.15, velocity=95)
    melody_inst.notes.extend(mel_s1)

    mel_s2 = contour("Em", "natural_minor", direction="ascending", num_notes=half * 3,
                     octave=4, seed=c.seed + 1, start_time=half * bar,
                     note_duration=beat * 0.45, note_gap=beat * 0.12, velocity=105)
    for n in mel_s2:
        if n.start < c.duration:
            melody_inst.notes.append(n)

    # Spike at halfway
    mid = half * bar
    if mid < c.duration:
        spike_notes = spike(base_pitch=64, interval="P5", start=mid, velocity=115)
        for n in spike_notes:
            if n.start < c.duration:
                melody_inst.notes.append(n)

    # Blast at bar 11
    s_blast = 11 * bar
    if s_blast < c.duration:
        bl = blast(bars=min(3, int((c.duration - s_blast) / bar)), tempo=138, time_sig=(4, 4), seed=c.seed + 2)
        for n in bl:
            n.start += s_blast
            n.end += s_blast
            n.velocity = min(127, n.velocity + 20)
            if n.start < c.duration:
                drums_inst.notes.append(n)

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
