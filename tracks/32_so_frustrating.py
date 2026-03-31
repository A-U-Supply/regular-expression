#!/usr/bin/env python
"""Track 32: so frustrating — Deflation begins. Energy draining. Bm Dorian, 118bpm.
A loop slowly falls apart. Loop That Breaks."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_FINGER, GUITAR_DISTORTION, GUITAR_OVERDRIVE,
                           DRUM_CHANNEL, CRASH, KICK, SNARE)
from lib.drums import driving_emo, half_time, no_snare, floor_tom_pulse
from lib.harmony import chord
from lib.melody import contour, broken_trail, phrase
from lib.bass import locked_bass, counter_melody
from lib.humanize import strum, humanize_velocity, SeededRng
from lib.directives import loop_that_breaks
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(32, "so_frustrating", key="Bm", tempo=118, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_FINGER)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    # Bm Dorian: B C# D E F# G# A
    chord_seq = [("B", "min"), ("E", "min"), ("F#", "min"), ("B", "min")]
    bm_root = 35  # B1

    # === Base 2-bar loop ===
    loop_dur = 2 * bar

    base_mel = contour("Bm", "dorian", direction="ascending", num_notes=6,
                       octave=4, seed=c.seed, start_time=0.0,
                       note_duration=beat * 0.7, note_gap=beat * 0.25, velocity=85)

    # 4 mutating repetitions (loop degrades)
    loop_reps = loop_that_breaks(base_mel, repetitions=4, seed=c.seed)

    # === Section 1: 4 × 2-bar loops, progressively deflationary ===
    for rep_idx, rep_notes in enumerate(loop_reps):
        time_offset = rep_idx * loop_dur

        # Drums deflate: full → half_time → no_snare → floor_tom only
        if rep_idx == 0:
            dr = driving_emo(bars=2, tempo=118, time_sig=(4, 4), seed=c.seed + rep_idx)
        elif rep_idx == 1:
            dr = half_time(bars=2, tempo=118, time_sig=(4, 4), seed=c.seed + rep_idx)
        elif rep_idx == 2:
            dr = no_snare(bars=2, tempo=118, time_sig=(4, 4), seed=c.seed + rep_idx)
            for n in dr:
                n.velocity = max(1, n.velocity - 20)
        else:
            dr = floor_tom_pulse(bars=2, tempo=118, time_sig=(4, 4), seed=c.seed + rep_idx)
            for n in dr:
                n.velocity = max(1, n.velocity - 30)

        for n in dr:
            n.start += time_offset
            n.end += time_offset
        drums_inst.notes.extend(dr)

        # Melody
        for n in rep_notes:
            melody_inst.notes.append(pretty_midi.Note(
                velocity=max(1, min(127, n.velocity - rep_idx * 10)),
                pitch=max(0, min(127, n.pitch)),
                start=n.start + time_offset,
                end=n.end + time_offset,
            ))

        # Chords: fade
        for ci in range(2):
            t = time_offset + ci * bar
            root, q = chord_seq[ci % 4]
            pitches = chord(root, q, octave=2, voicing="open")
            vel = max(35, 80 - rep_idx * 14)
            cn = [pretty_midi.Note(velocity=vel, pitch=p, start=t, end=t + bar * 0.85) for p in pitches]
            chords_inst.notes.extend(strum(cn, direction="down", spread_ms=25 + rep_idx * 10))

        # Bass
        kick_t = [time_offset + i * bar + b * beat for i in range(2) for b in [0, 2]]
        bass_rep = locked_bass(kick_t, root=bm_root, fifth=42, bars=2, tempo=118,
                               seed=c.seed + rep_idx, velocity=max(40, 90 - rep_idx * 14))
        bass_inst.notes.extend(bass_rep)

    # === Section 2: Everything drained — just counter melody bass ===
    s2 = 4 * loop_dur
    s2_bars = max(1, int((c.duration - s2) / bar))

    cm_bass = counter_melody("Bm", "dorian", bars=s2_bars, tempo=118,
                              time_sig=(4, 4), seed=c.seed + 4, velocity=55)
    for n in cm_bass:
        t = n.start + s2
        if t < c.duration:
            bass_inst.notes.append(pretty_midi.Note(
                velocity=n.velocity, pitch=n.pitch,
                start=t, end=min(n.end + s2, c.duration),
            ))

    # Very sparse chords
    if s2 < c.duration:
        pitches = chord("B", "min", octave=2, voicing="open")
        for p in pitches:
            chords_inst.notes.append(pretty_midi.Note(velocity=25, pitch=p,
                                      start=s2, end=min(c.duration, s2 + 2 * bar)))

    # Broken trail melody ending
    mel_end = contour("Bm", "dorian", direction="descending", num_notes=6,
                      octave=4, seed=c.seed + 5, start_time=s2,
                      note_duration=beat * 0.8, note_gap=beat * 0.5, velocity=55)
    mel_broken = broken_trail(mel_end, decay_point=3)
    for n in mel_broken:
        if n.start < c.duration:
            melody_inst.notes.append(n)

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
