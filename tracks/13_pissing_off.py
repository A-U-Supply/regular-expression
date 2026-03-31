#!/usr/bin/env python
"""Track 13: pissing off — Conjugation trilogy pt 3. Same material as 11 inverted.
Starts full, strips away. Slower, 7/8. Am natural minor."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import importlib.util
import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_FINGER, LEAD_SQUARE, GUITAR_OVERDRIVE,
                           DRUM_CHANNEL, CRASH, KICK, FLOOR_TOM)
from lib.drums import driving_emo, half_time, floor_tom_pulse
from lib.harmony import chord
from lib.melody import contour, broken_trail
from lib.bass import locked_bass
from lib.humanize import strum, humanize_velocity, SeededRng
from lib.directives import reverse_structure_plan
from lib.cli import parse_track_args

# Import shared melodic material from track 11
_t11_spec = importlib.util.spec_from_file_location(
    "track_11", Path(__file__).parent / "11_piss_off.py")
_t11 = importlib.util.module_from_spec(_t11_spec)
_t11_spec.loader.exec_module(_t11)
TRILOGY_MELODY_PITCHES = _t11.TRILOGY_MELODY_PITCHES

# Am transposition: Em→Am is 5 semitones up
AM_MELODY_PITCHES = [p + 5 for p in TRILOGY_MELODY_PITCHES]  # Transposed to Am
AM_ROOT = 33  # A1


def generate(seed=None):
    c = Composer(13, "pissing_off", key="Am", tempo=116, time_sig=(7, 8), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration  # eighth note at 116bpm
    bar = c.bar_duration   # 7 eighths

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_FINGER)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=LEAD_SQUARE)

    am_chord_seq = [("A", "min"), ("C", "min"), ("G", "min"), ("E", "min")]

    # Calculate how many bars we have
    total_bars = c.bars  # ~14 bars

    # === Reverse structure: start full, strip away ===
    # Section 1: Bars 1-5 — Full band, fortissimo
    s1 = 0.0
    s1_bars = 5

    de = driving_emo(bars=s1_bars, tempo=116, time_sig=(7, 8), seed=c.seed)
    drums_inst.notes.extend(de)

    kick_times = [i * bar + b * beat for i in range(s1_bars) for b in [0, 2, 4]]
    bass_s1 = locked_bass(kick_times, root=AM_ROOT, fifth=40, bars=s1_bars,
                          tempo=116, seed=c.seed, velocity=105)
    bass_inst.notes.extend(bass_s1)

    for i in range(s1_bars):
        t = i * bar
        root, q = am_chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=95 + rng.randint(-5, 5), pitch=p,
                               start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=20))

    # Melody from shared material (transposed)
    mel_t = 0.0
    for pitch in AM_MELODY_PITCHES:
        melody_inst.notes.append(pretty_midi.Note(velocity=100, pitch=max(0, min(127, pitch)),
                                  start=mel_t, end=mel_t + beat * 1.2))
        mel_t += beat * 1.5

    # === Section 2: Bars 6-9 — Drums drop, others continue ===
    s2 = s1_bars * bar
    s2_bars = 4

    for i in range(s2_bars):
        t = s2 + i * bar
        root, q = am_chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=80, pitch=p, start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=30))
        bass_inst.notes.append(pretty_midi.Note(velocity=85, pitch=AM_ROOT,
                               start=t, end=t + bar * 0.7))

    # Melody with broken trail (fading)
    mel_notes_s2 = []
    mel_t2 = s2
    for pitch in AM_MELODY_PITCHES:
        mel_notes_s2.append(pretty_midi.Note(velocity=85, pitch=max(0, min(127, pitch)),
                             start=mel_t2, end=mel_t2 + beat * 1.2))
        mel_t2 += beat * 1.5

    mel_broken = broken_trail(mel_notes_s2, decay_point=6)
    melody_inst.notes.extend(mel_broken)

    # === Section 3: Bars 10-12 — Chords drop, just bass + fading melody ===
    s3 = (s1_bars + s2_bars) * bar
    s3_bars = 3

    for i in range(s3_bars):
        t = s3 + i * bar
        if t >= c.duration:
            break
        bass_inst.notes.append(pretty_midi.Note(velocity=65, pitch=AM_ROOT,
                               start=t, end=min(t + bar * 0.8, c.duration)))

    # Single fading melody note
    melody_inst.notes.append(pretty_midi.Note(velocity=40, pitch=69,  # A4
                              start=s3, end=min(s3 + 2 * bar, c.duration)))

    # Floor tom sparse pulse in section 3
    ft = floor_tom_pulse(bars=min(s3_bars, 3), tempo=116, time_sig=(7, 8), seed=c.seed + 2)
    for n in ft:
        n.start += s3
        n.end += s3
        if n.start < c.duration:
            drums_inst.notes.append(n)

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
