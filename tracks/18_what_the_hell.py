#!/usr/bin/env python
"""Track 18: what the hell — Twin B. Exhausted. Bm Dorian, 96bpm. Reverse structure.
Same melody contour as track 17 but slow, in Dorian, decaying."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import importlib.util
import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_FINGER, GUITAR_DISTORTION, PAD_WARM,
                           DRUM_CHANNEL, CRASH, KICK, FLOOR_TOM)
from lib.drums import half_time, floor_tom_pulse
from lib.harmony import chord
from lib.melody import contour, broken_trail
from lib.bass import locked_bass
from lib.humanize import strum, SeededRng
from lib.directives import reverse_structure_plan
from lib.cli import parse_track_args

# Import shared twin melody from track 17
_t17_spec = importlib.util.spec_from_file_location(
    "track_17", Path(__file__).parent / "17_what_the_fuck.py")
_t17 = importlib.util.module_from_spec(_t17_spec)
_t17_spec.loader.exec_module(_t17)
TWIN_MELODY_PITCHES = _t17.TWIN_MELODY_PITCHES


def generate(seed=None):
    c = Composer(18, "what_the_hell", key="Bm", tempo=96, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_FINGER)
    chords_inst = c.add_instrument("Chords", program=PAD_WARM)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    # Bm Dorian: B C# D E F# G# A
    chord_seq = [("B", "min"), ("E", "min"), ("A", "min"), ("B", "min")]
    bm_root = 35  # B1

    # === Section 1: Bars 1-4 — Full band, moderate (starting "high") ===
    s1 = 0.0
    ht = half_time(bars=4, tempo=96, time_sig=(4, 4), seed=c.seed)
    drums_inst.notes.extend(ht)

    kick_times = [i * bar + b * beat for i in range(4) for b in [0, 2]]
    bass_s1 = locked_bass(kick_times, root=bm_root, fifth=42, bars=4,
                          tempo=96, seed=c.seed, velocity=85)
    bass_inst.notes.extend(bass_s1)

    for i in range(4):
        t = i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=75 + rng.randint(-5, 5), pitch=p,
                               start=t, end=t + bar * 0.9) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=40))

    # Twin melody — slow version, same pitches but sustained
    mel_t = 0.0
    for pitch in TWIN_MELODY_PITCHES:
        melody_inst.notes.append(pretty_midi.Note(velocity=80, pitch=pitch,
                                  start=mel_t, end=mel_t + beat * 1.5))
        mel_t += beat * 1.8

    # === Section 2: Bars 5-8 — Drums drop to floor tom, melody fades ===
    s2 = 4 * bar
    ft = floor_tom_pulse(bars=4, tempo=96, time_sig=(4, 4), seed=c.seed + 1)
    for n in ft:
        n.start += s2
        n.end += s2
        n.velocity = max(1, n.velocity - 20)
    drums_inst.notes.extend(ft)

    for i in range(4):
        t = s2 + i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=60, pitch=p, start=t, end=t + bar * 0.9) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=45))

    kick_times_s2 = [s2 + i * bar + b * beat for i in range(4) for b in [0, 2]]
    bass_s2 = locked_bass(kick_times_s2, root=bm_root, fifth=42, bars=4,
                          tempo=96, seed=c.seed + 1, velocity=65)
    bass_inst.notes.extend(bass_s2)

    # Melody with broken trail
    mel_s2 = []
    mel_t2 = s2
    for pitch in TWIN_MELODY_PITCHES:
        mel_s2.append(pretty_midi.Note(velocity=70, pitch=pitch,
                       start=mel_t2, end=mel_t2 + beat * 1.5))
        mel_t2 += beat * 2.0

    mel_broken = broken_trail(mel_s2, decay_point=8)
    melody_inst.notes.extend(mel_broken)

    # === Section 3: Bars 9-11 — Just bass + pad chord, very quiet ===
    s3 = 8 * bar
    s3_bars = 3

    for i in range(s3_bars):
        t = s3 + i * bar
        if t >= c.duration:
            break
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=1, voicing="open")
        cn = [pretty_midi.Note(velocity=35, pitch=p, start=t,
                               end=min(t + bar * 0.9, c.duration)) for p in pitches]
        chords_inst.notes.extend(cn)
        bass_inst.notes.append(pretty_midi.Note(velocity=40, pitch=bm_root,
                               start=t, end=min(t + bar * 0.8, c.duration)))

    # === Section 4: Bars 12-14 — Total decay, drone-like pad ===
    s4 = 11 * bar
    if s4 < c.duration:
        pitches = chord("B", "min7", octave=1, voicing="open")
        for p in pitches:
            chords_inst.notes.append(pretty_midi.Note(velocity=20, pitch=max(0, p - 12),
                                      start=s4, end=min(c.duration, s4 + 3 * bar)))

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
