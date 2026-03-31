#!/usr/bin/env python
"""Track 12: pissed off — Conjugation trilogy pt 2. Same material as track 11
shifted to Bm, faster at 148bpm. Melody rhythmically displaced."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import importlib.util
import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_PICK, GUITAR_DISTORTION, GUITAR_OVERDRIVE,
                           DRUM_CHANNEL, CRASH, KICK)
from lib.drums import driving_emo, blast
from lib.harmony import chord
from lib.melody import contour
from lib.bass import locked_bass, driving_eighths
from lib.humanize import strum, humanize_velocity, SeededRng
from lib.directives import rhythmic_displacement
from lib.cli import parse_track_args

# Import shared melodic material from track 11
_t11_spec = importlib.util.spec_from_file_location(
    "track_11", Path(__file__).parent / "11_piss_off.py")
_t11 = importlib.util.module_from_spec(_t11_spec)
_t11_spec.loader.exec_module(_t11)
TRILOGY_MELODY_PITCHES = _t11.TRILOGY_MELODY_PITCHES

# Bm transposition: Em→Bm is a 5th up (7 semitones)
BM_MELODY_PITCHES = [p + 7 for p in TRILOGY_MELODY_PITCHES]  # Transposed to Bm
BM_ROOT = 35  # B1


def generate(seed=None):
    c = Composer(12, "pissed_off", key="Bm", tempo=148, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_PICK)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    bm_chord_seq = [("B", "min"), ("D", "min"), ("A", "min"), ("E", "min")]

    # === Section 1: Full band driving — 8 bars ===
    s1 = 0.0
    de = driving_emo(bars=8, tempo=148, time_sig=(4, 4), seed=c.seed)
    drums_inst.notes.extend(de)

    kick_times = [i * bar + b * beat for i in range(8) for b in [0, 2]]
    bass_s1 = locked_bass(kick_times, root=BM_ROOT, fifth=42, bars=8,
                          tempo=148, seed=c.seed, velocity=100)
    bass_inst.notes.extend(bass_s1)

    for i in range(8):
        t = i * bar
        root, q = bm_chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=90 + rng.randint(-5, 5), pitch=p,
                               start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=20))

    # Melody from shared material (transposed) — then displaced
    mel_notes_s1 = []
    mel_t = 0.0
    for pitch in BM_MELODY_PITCHES:
        mel_notes_s1.append(pretty_midi.Note(velocity=90, pitch=max(0, min(127, pitch)),
                             start=mel_t, end=mel_t + beat * 0.7))
        mel_t += beat

    mel_displaced_s1 = rhythmic_displacement(mel_notes_s1, offset_eighths=2, tempo=148)
    melody_inst.notes.extend(mel_displaced_s1)

    # === Section 2: 4 bars blast ===
    s2 = 8 * bar
    bl = blast(bars=4, tempo=148, time_sig=(4, 4), seed=c.seed + 1)
    for n in bl:
        n.start += s2
        n.end += s2
        n.velocity = min(127, n.velocity + 10)
    drums_inst.notes.extend(bl)

    kick_times_s2 = [s2 + i * bar + b * beat for i in range(4) for b in [0, 2]]
    bass_s2 = locked_bass(kick_times_s2, root=BM_ROOT, fifth=42, bars=4,
                          tempo=148, seed=c.seed + 1, velocity=115)
    bass_inst.notes.extend(bass_s2)

    for i in range(4):
        t = s2 + i * bar
        root, q = bm_chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="closed")
        cn = [pretty_midi.Note(velocity=110, pitch=p, start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=15))

    mel_notes_s2 = []
    mel_t2 = 0.0
    for pitch in BM_MELODY_PITCHES:
        mel_notes_s2.append(pretty_midi.Note(velocity=105, pitch=max(0, min(127, pitch + 12)),
                             start=mel_t2, end=mel_t2 + beat * 0.5))
        mel_t2 += beat * 0.75

    mel_displaced_s2 = rhythmic_displacement(mel_notes_s2, offset_eighths=1, tempo=148)
    for n in mel_displaced_s2:
        melody_inst.notes.append(pretty_midi.Note(
            velocity=n.velocity, pitch=n.pitch,
            start=n.start + s2, end=n.end + s2,
        ))

    # === Section 3: 2 bars — crash and final chord ===
    s3 = 12 * bar
    if s3 < c.duration:
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=CRASH,
                                start=s3, end=s3 + 0.4))
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=KICK,
                                start=s3, end=s3 + 0.1))

        de_s3 = driving_emo(bars=2, tempo=148, time_sig=(4, 4), seed=c.seed + 2)
        for n in de_s3:
            n.start += s3
            n.end += s3
            n.velocity = min(127, n.velocity + 20)
            if n.start < c.duration:
                drums_inst.notes.append(n)

        pitches = chord("B", "min", octave=2, voicing="closed")
        for p in pitches:
            chords_inst.notes.append(pretty_midi.Note(velocity=120, pitch=p,
                                      start=s3, end=min(c.duration, s3 + bar)))
        bass_inst.notes.append(pretty_midi.Note(velocity=120, pitch=BM_ROOT,
                               start=s3, end=min(c.duration, s3 + bar)))
        melody_inst.notes.append(pretty_midi.Note(velocity=120, pitch=71,  # B4
                                  start=s3, end=min(c.duration, s3 + beat * 2)))

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
