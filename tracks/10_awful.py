#!/usr/bin/env python
"""Track 10: awful — Seasick 6/8. Everything collapses to unison on B midway,
then blasts into eruption. Waltz feel warping under pressure."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_FINGER, GUITAR_DISTORTION, GUITAR_CLEAN,
                           DRUM_CHANNEL, CRASH, KICK, FLOOR_TOM)
from lib.drums import driving_emo, blast, half_time
from lib.harmony import chord
from lib.melody import contour, phrase
from lib.bass import locked_bass, driving_eighths
from lib.humanize import strum, humanize_velocity, SeededRng
from lib.directives import unison_collapse
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(10, "awful", key="Bm", tempo=110, time_sig=(6, 8), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration  # 6/8 bar = 3 beats at 110 bpm (dotted quarter = 2 eighth notes)

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_FINGER)
    chords_inst = c.add_instrument("Chords", program=GUITAR_CLEAN)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    # B Phrygian: B C D E F# G A
    chord_seq = [("B", "min"), ("C", "min"), ("F#", "min"), ("B", "min")]

    # === Section 1: Bars 1-4 — Waltz clean ===
    s1 = 0.0
    ht = half_time(bars=4, tempo=110, time_sig=(6, 8), seed=c.seed)
    drums_inst.notes.extend(ht)

    for i in range(4):
        t = s1 + i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=70 + rng.randint(-5, 5), pitch=p,
                               start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=30))
        bass_inst.notes.append(pretty_midi.Note(velocity=75, pitch=[35, 36, 30, 35][i],
                               start=t, end=t + bar * 0.7))

    mel_s1 = contour("Bm", "phrygian", direction="ascending", num_notes=10,
                     octave=4, seed=c.seed, start_time=s1,
                     note_duration=beat * 0.8, note_gap=beat * 0.3, velocity=80)
    melody_inst.notes.extend(mel_s1)

    # === Section 2: Bars 5-8 — Intensify ===
    s2 = 4 * bar
    de = driving_emo(bars=4, tempo=110, time_sig=(6, 8), seed=c.seed + 1)
    for n in de:
        n.start += s2
        n.end += s2
    drums_inst.notes.extend(de)

    for i in range(4):
        t = s2 + i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=90 + rng.randint(-5, 5), pitch=p,
                               start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=20))

    kick_times_s2 = [s2 + i * bar + b * beat for i in range(4) for b in [0, 2]]
    bass_s2 = locked_bass(kick_times_s2, root=35, fifth=42, bars=4, tempo=110,
                          seed=c.seed + 1, velocity=100)
    bass_inst.notes.extend(bass_s2)

    mel_s2 = contour("Bm", "phrygian", direction="descending", num_notes=12,
                     octave=5, seed=c.seed + 1, start_time=s2,
                     note_duration=beat * 0.6, note_gap=beat * 0.2, velocity=95)
    melody_inst.notes.extend(mel_s2)

    # === Section 3: Bars 9-10 — Unison collapse on B ===
    s3 = 8 * bar
    # B pitch at multiple octaves: B2=47, B3=59, B4=71
    unison_notes = unison_collapse(target_pitch=47, num_instruments=4,
                                   start=s3, duration=2 * bar, velocity=115)
    # Distribute to instruments
    bass_inst.notes.append(pretty_midi.Note(velocity=115, pitch=35,  # B1
                            start=s3, end=s3 + 2 * bar))
    chords_inst.notes.append(pretty_midi.Note(velocity=115, pitch=47,  # B2
                             start=s3, end=s3 + 2 * bar))
    melody_inst.notes.append(pretty_midi.Note(velocity=115, pitch=59,  # B3
                              start=s3, end=s3 + 2 * bar))
    # Floor tom pulse in unison section
    for beat_idx in range(12):  # 2 bars × 6 beats
        t_ft = s3 + beat_idx * beat
        drums_inst.notes.append(pretty_midi.Note(velocity=100 + rng.randint(-10, 10),
                                  pitch=FLOOR_TOM, start=t_ft, end=t_ft + 0.1))

    # === Section 4: Bars 11-14 — Blast eruption ===
    s4 = 10 * bar
    bl = blast(bars=4, tempo=110, time_sig=(6, 8), seed=c.seed + 2)
    for n in bl:
        n.start += s4
        n.end += s4
        n.velocity = min(127, n.velocity + 20)
    drums_inst.notes.extend(bl)

    for i in range(4):
        t = s4 + i * bar
        if t >= c.duration:
            break
        pitches = chord("B", "min", octave=2, voicing="closed")
        cn = [pretty_midi.Note(velocity=120, pitch=p, start=t,
                               end=min(t + bar * 0.9, c.duration)) for p in pitches]
        chords_inst.notes.extend(cn)
        bass_inst.notes.append(pretty_midi.Note(velocity=120, pitch=35,
                               start=t, end=min(t + bar, c.duration)))

    mel_s4 = contour("Bm", "phrygian", direction="ascending", num_notes=12,
                     octave=4, seed=c.seed + 2, start_time=s4,
                     note_duration=beat * 0.4, note_gap=beat * 0.1, velocity=115)
    for n in mel_s4:
        if n.start < c.duration:
            melody_inst.notes.append(n)

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
