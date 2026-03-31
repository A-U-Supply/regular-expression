#!/usr/bin/env python
"""Track 14: piece of shit — Degradation trilogy starts aggressive. Dm Phrygian,
155bpm. 6 bars driving fury → collapse to solo melody → re-entry fortissimo."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_PICK, GUITAR_DISTORTION, GUITAR_OVERDRIVE,
                           DRUM_CHANNEL, CRASH, KICK, FLOOR_TOM)
from lib.drums import driving_emo, blast
from lib.harmony import chord
from lib.melody import contour, spike
from lib.bass import locked_bass, driving_eighths
from lib.humanize import strum, humanize_velocity, SeededRng
from lib.directives import collapse_plan
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(14, "piece_of_shit", key="Dm", tempo=155, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_PICK)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    # Dm Phrygian: D Eb F G A Bb C
    chord_seq = [("D", "min"), ("Eb", "min"), ("A", "min"), ("D", "min")]

    # === Section 1: Bars 1-6 — Driving fury ===
    s1 = 0.0
    bl = blast(bars=4, tempo=155, time_sig=(4, 4), seed=c.seed)
    drums_inst.notes.extend(bl)

    de_extra = driving_emo(bars=2, tempo=155, time_sig=(4, 4), seed=c.seed + 10)
    for n in de_extra:
        n.start += 4 * bar
        n.end += 4 * bar
        n.velocity = min(127, n.velocity + 15)
    drums_inst.notes.extend(de_extra)

    kick_times = [i * bar + b * beat for i in range(6) for b in [0, 2]]
    bass_s1 = locked_bass(kick_times, root=38, fifth=45, bars=6,
                          tempo=155, seed=c.seed, velocity=115)
    bass_inst.notes.extend(bass_s1)

    for i in range(6):
        t = i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="closed")
        cn = [pretty_midi.Note(velocity=105 + rng.randint(-5, 5), pitch=p,
                               start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=15))

    mel_s1 = contour("Dm", "phrygian", direction="descending", num_notes=16,
                     octave=4, seed=c.seed, start_time=s1,
                     note_duration=beat * 0.5, note_gap=beat * 0.1, velocity=110)
    melody_inst.notes.extend(mel_s1)

    # === Section 2: Bars 7-9 — Collapse to solo melody ===
    s2 = 6 * bar
    mel_s2 = contour("Dm", "phrygian", direction="ascending", num_notes=10,
                     octave=3, seed=c.seed + 1, start_time=s2,
                     note_duration=beat * 0.7, note_gap=beat * 0.25, velocity=70)
    melody_inst.notes.extend(mel_s2)

    # Solo bass note at very low velocity
    bass_inst.notes.append(pretty_midi.Note(velocity=45, pitch=38,
                           start=s2, end=s2 + bar))

    # === Section 3: Bars 10-13 — Re-entry fortissimo ===
    s3 = 9 * bar
    if s3 < c.duration:
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=CRASH,
                                start=s3, end=s3 + 0.4))
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=KICK,
                                start=s3, end=s3 + 0.1))

        bl_s3 = blast(bars=4, tempo=155, time_sig=(4, 4), seed=c.seed + 2)
        for n in bl_s3:
            n.start += s3
            n.end += s3
            n.velocity = min(127, n.velocity + 20)
            if n.start < c.duration:
                drums_inst.notes.append(n)

        kick_times_s3 = [s3 + i * bar + b * beat for i in range(4) for b in [0, 2]]
        bass_s3 = locked_bass(kick_times_s3, root=38, fifth=45, bars=4,
                              tempo=155, seed=c.seed + 2, velocity=125)
        for n in bass_s3:
            if n.start < c.duration:
                bass_inst.notes.append(n)

        for i in range(4):
            t = s3 + i * bar
            if t >= c.duration:
                break
            pitches = chord("D", "min", octave=2, voicing="closed")
            cn = [pretty_midi.Note(velocity=120, pitch=p, start=t,
                                   end=min(t + bar * 0.9, c.duration)) for p in pitches]
            chords_inst.notes.extend(cn)

        # Spike at re-entry
        spike_notes = spike(base_pitch=62, interval="min7", start=s3, velocity=127)
        for n in spike_notes:
            if n.start < c.duration:
                melody_inst.notes.append(n)

        mel_s3 = contour("Dm", "phrygian", direction="descending", num_notes=12,
                         octave=5, seed=c.seed + 3, start_time=s3 + beat,
                         note_duration=beat * 0.4, note_gap=beat * 0.1, velocity=120)
        for n in mel_s3:
            if n.start < c.duration:
                melody_inst.notes.append(n)

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
