#!/usr/bin/env python
"""Track 22: fuck awful — Lurching 5/4 loop that falls apart. Em natural minor.
Loop That Breaks directive — 5/4 makes it stumble."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_FINGER, GUITAR_DISTORTION, GUITAR_OVERDRIVE,
                           DRUM_CHANNEL, CRASH, KICK, SNARE)
from lib.drums import driving_emo, no_snare, half_time
from lib.harmony import chord
from lib.melody import contour, broken_trail, stutter
from lib.bass import locked_bass, counter_melody
from lib.humanize import strum, humanize_velocity, SeededRng
from lib.directives import loop_that_breaks
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(22, "fuck_awful", key="Em", tempo=115, time_sig=(5, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration  # 5 beats

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_FINGER)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    # Em natural minor
    chord_seq = [("E", "min"), ("G", "min"), ("D", "min"), ("A", "min"), ("E", "min")]
    em_root = 28  # E1

    # === Base 2-bar loop ===
    loop_dur = 2 * bar

    base_mel = contour("Em", "natural_minor", direction="ascending", num_notes=7,
                       octave=4, seed=c.seed, start_time=0.0,
                       note_duration=beat * 0.6, note_gap=beat * 0.2, velocity=90)

    # 4 mutating repetitions
    loop_reps = loop_that_breaks(base_mel, repetitions=4, seed=c.seed)

    # === Section 1: 4 × 2-bar loops with degrading drums ===
    for rep_idx, rep_notes in enumerate(loop_reps):
        time_offset = rep_idx * loop_dur

        # Drum patterns degrade: full → no_snare → half_time → just kick
        if rep_idx == 0:
            dr = driving_emo(bars=2, tempo=115, time_sig=(5, 4), seed=c.seed + rep_idx)
        elif rep_idx == 1:
            dr = driving_emo(bars=2, tempo=115, time_sig=(5, 4), seed=c.seed + rep_idx)
            for n in dr:
                if n.pitch == SNARE:
                    n.velocity = max(1, n.velocity - 40)  # Ghost the snare
        elif rep_idx == 2:
            dr = no_snare(bars=2, tempo=115, time_sig=(5, 4), seed=c.seed + rep_idx)
        else:
            dr = half_time(bars=2, tempo=115, time_sig=(5, 4), seed=c.seed + rep_idx)
            for n in dr:
                n.velocity = max(1, n.velocity - 30)

        for n in dr:
            n.start += time_offset
            n.end += time_offset
        drums_inst.notes.extend(dr)

        # Melody mutations
        for n in rep_notes:
            melody_inst.notes.append(pretty_midi.Note(
                velocity=max(1, min(127, n.velocity - rep_idx * 8)),
                pitch=max(0, min(127, n.pitch)),
                start=n.start + time_offset,
                end=n.end + time_offset,
            ))

        # Chords per loop
        for ci in range(2):
            t = time_offset + ci * bar
            root, q = chord_seq[ci % len(chord_seq)]
            pitches = chord(root, q, octave=2, voicing="open")
            vel = max(40, 85 - rep_idx * 12)
            cn = [pretty_midi.Note(velocity=vel, pitch=p, start=t, end=t + bar * 0.85) for p in pitches]
            chords_inst.notes.extend(strum(cn, direction="down", spread_ms=20 + rep_idx * 8))

        # Bass
        kick_t = [time_offset + i * 5 * beat + b * beat for i in range(2) for b in [0, 2, 4]]
        bass_rep = locked_bass(kick_t, root=em_root, fifth=35, bars=2, tempo=115,
                               seed=c.seed + rep_idx, velocity=max(50, 95 - rep_idx * 12))
        bass_inst.notes.extend(bass_rep)

    # === Section 2: Everything collapses — counter melody bass, no drums ===
    s2 = 4 * loop_dur
    s2_bars = max(1, int((c.duration - s2) / bar))

    cm_bass = counter_melody("Em", "natural_minor", bars=s2_bars, tempo=115,
                             time_sig=(5, 4), seed=c.seed + 4, velocity=60)
    for n in cm_bass:
        t = n.start + s2
        if t < c.duration:
            bass_inst.notes.append(pretty_midi.Note(
                velocity=n.velocity, pitch=n.pitch,
                start=t, end=min(n.end + s2, c.duration),
            ))

    # Single fading chord
    if s2 < c.duration:
        pitches = chord("E", "min", octave=2, voicing="open")
        for p in pitches:
            chords_inst.notes.append(pretty_midi.Note(velocity=35, pitch=p,
                                      start=s2, end=min(c.duration, s2 + s2_bars * bar)))

    # Broken trail melody
    mel_s2 = contour("Em", "natural_minor", direction="descending", num_notes=8,
                     octave=4, seed=c.seed + 5, start_time=s2,
                     note_duration=beat * 0.7, note_gap=beat * 0.3, velocity=70)
    mel_broken = broken_trail(mel_s2, decay_point=4)
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
