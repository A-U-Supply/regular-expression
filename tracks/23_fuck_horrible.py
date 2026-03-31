#!/usr/bin/env python
"""Track 23: fuck horrible — 7/8 with displaced drums. Persistent wrongness.
Bm Phrygian, 135bpm. Rhythmic Displacement (drums displaced)."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_PICK, GUITAR_DISTORTION, GUITAR_OVERDRIVE,
                           DRUM_CHANNEL, CRASH, KICK, SNARE, HAT_CLOSED)
from lib.drums import driving_emo, blast, no_snare
from lib.harmony import chord
from lib.melody import contour, stutter, spike
from lib.bass import locked_bass, driving_eighths
from lib.humanize import strum, humanize_velocity, SeededRng
from lib.directives import rhythmic_displacement
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(23, "fuck_horrible", key="Bm", tempo=135, time_sig=(7, 8), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration  # eighth note at 135bpm
    bar = c.bar_duration   # 7 eighths

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_PICK)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    # Bm Phrygian: B C D E F# G A
    chord_seq = [("B", "min"), ("C", "min"), ("F#", "min"), ("B", "min")]
    bm_root = 35  # B1

    total_bars = c.bars  # ~14-16 bars

    # === Build drum pattern and displace it ===
    # Generate drums normally first
    de = driving_emo(bars=total_bars, tempo=135, time_sig=(7, 8), seed=c.seed)

    # Displace drums by 1 eighth note (creates persistent wrongness)
    # Manual displacement: shift all drum notes by one eighth duration
    eighth_dur = beat  # in 7/8, beat IS eighth note
    displaced_drums = []
    for n in de:
        new_start = max(0.0, n.start + eighth_dur)
        new_end = new_start + (n.end - n.start)
        displaced_drums.append(pretty_midi.Note(
            velocity=n.velocity, pitch=n.pitch,
            start=new_start, end=new_end,
        ))
    drums_inst.notes.extend(displaced_drums)

    # === Bass follows normal grid (not displaced) ===
    kick_times = [i * bar + b * beat for i in range(total_bars) for b in [0, 2, 4]]
    bass_notes = locked_bass(kick_times, root=bm_root, fifth=42, bars=total_bars,
                             tempo=135, seed=c.seed, velocity=100)
    bass_inst.notes.extend(bass_notes)

    # === Chords: normal grid ===
    for i in range(total_bars):
        t = i * bar
        if t >= c.duration:
            break
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="closed")
        cn = [pretty_midi.Note(velocity=88 + rng.randint(-5, 5), pitch=p,
                               start=t, end=min(t + bar * 0.85, c.duration)) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=18))

    # === Melody normal, but asymmetric 7/8 phrasing ===
    # Two melody passes across the track
    half = total_bars // 2

    mel_s1 = contour("Bm", "phrygian", direction="descending", num_notes=half * 4,
                     octave=4, seed=c.seed, start_time=0.0,
                     note_duration=beat * 0.8, note_gap=beat * 0.15, velocity=95)
    melody_inst.notes.extend(mel_s1)

    mel_s2 = contour("Bm", "phrygian", direction="ascending", num_notes=half * 4,
                     octave=4, seed=c.seed + 1, start_time=half * bar,
                     note_duration=beat * 0.6, note_gap=beat * 0.2, velocity=105)
    for n in mel_s2:
        if n.start < c.duration:
            melody_inst.notes.append(n)

    # Spike at midpoint
    mid = half * bar
    if mid < c.duration:
        spike_notes = spike(base_pitch=59, interval="P5", start=mid, velocity=115)
        for n in spike_notes:
            if n.start < c.duration:
                melody_inst.notes.append(n)

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
