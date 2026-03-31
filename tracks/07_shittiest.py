#!/usr/bin/env python
"""Track 07: shittiest — Sinking trilogy finale. Reverse structure: starts at climax,
strips away instrument by instrument. Everything falls apart in sequence."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_FINGER, GUITAR_DISTORTION, PAD_WARM,
                           DRUM_CHANNEL, CRASH, KICK, FLOOR_TOM)
from lib.drums import driving_emo, half_time, floor_tom_pulse
from lib.harmony import chord
from lib.melody import contour, broken_trail
from lib.bass import locked_bass
from lib.humanize import humanize_velocity, strum, SeededRng
from lib.directives import drone, reverse_structure_plan
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(7, "shittiest", key="Am", tempo=90, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_FINGER)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)
    pad_inst = c.add_instrument("Pad", program=PAD_WARM)

    # Am natural minor: i-III-VII-iv = Am-C-G-Dm
    chord_seq = [("A", "min"), ("C", "min"), ("G", "min"), ("D", "min")]

    # === Section 1: Bars 1-4 — All instruments fortissimo (climax) ===
    s1 = 0.0
    de = driving_emo(bars=4, tempo=90, time_sig=(4, 4), seed=c.seed)
    for n in de:
        n.velocity = min(127, n.velocity + 20)
    drums_inst.notes.extend(de)

    kick_times = [s1 + i * bar + b * beat for i in range(4) for b in [0, 2]]
    bass_s1 = locked_bass(kick_times, root=33, fifth=40, bars=4, tempo=90, seed=c.seed, velocity=115)
    bass_inst.notes.extend(bass_s1)

    for i in range(4):
        t = s1 + i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=110 + rng.randint(-5, 5), pitch=p,
                               start=t, end=t + bar * 0.9) for p in pitches]
        pad_inst.notes.extend(strum(cn, direction="down", spread_ms=30))

    mel_s1 = contour("Am", "natural_minor", direction="descending", num_notes=14,
                     octave=5, seed=c.seed, start_time=s1,
                     note_duration=beat * 0.7, note_gap=beat * 0.2, velocity=110)
    melody_inst.notes.extend(mel_s1)

    # === Section 2: Bars 5-8 — Drums drop out, rest stays ===
    s2 = 4 * bar

    kick_times_2 = [s2 + i * bar + b * beat for i in range(4) for b in [0, 2]]
    bass_s2 = locked_bass(kick_times_2, root=33, fifth=40, bars=4, tempo=90, seed=c.seed + 1, velocity=100)
    bass_inst.notes.extend(bass_s2)

    for i in range(4):
        t = s2 + i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=90, pitch=p, start=t, end=t + bar * 0.9) for p in pitches]
        pad_inst.notes.extend(strum(cn, direction="down", spread_ms=35))

    mel_s2 = contour("Am", "natural_minor", direction="descending", num_notes=12,
                     octave=4, seed=c.seed + 1, start_time=s2,
                     note_duration=beat * 0.8, note_gap=beat * 0.3, velocity=95)
    melody_inst.notes.extend(mel_s2)

    # === Section 3: Bars 9-11 — Melody drops, just bass + pad ===
    s3 = 8 * bar
    bars_s3 = 3

    for i in range(bars_s3):
        t = s3 + i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=75, pitch=p, start=t, end=t + bar * 0.9) for p in pitches]
        pad_inst.notes.extend(strum(cn, direction="down", spread_ms=40))
        bass_inst.notes.append(pretty_midi.Note(velocity=80, pitch=33,
                               start=t, end=t + bar * 0.8))

    # === Section 4: Bars 12-13 — Bass drops, just pad ===
    s4 = 11 * bar
    bars_s4 = 2

    for i in range(bars_s4):
        t = s4 + i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        vel = max(1, 55 - i * 10)
        end_t = min(t + bar * 0.9, c.duration)
        if end_t <= t:
            continue
        cn = [pretty_midi.Note(velocity=vel, pitch=p, start=t, end=end_t) for p in pitches]
        pad_inst.notes.extend(strum(cn, direction="down", spread_ms=50))

    # === Section 5: Final — Pad fading alone ===
    s5 = 13 * bar
    if s5 < c.duration:
        root, q = chord_seq[0]
        pitches = chord(root, q, octave=1, voicing="open")
        for p in pitches:
            pad_inst.notes.append(pretty_midi.Note(velocity=30, pitch=p,
                                   start=s5, end=min(c.duration, s5 + 2 * bar)))

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
