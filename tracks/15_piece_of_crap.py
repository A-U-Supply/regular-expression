#!/usr/bin/env python
"""Track 15: piece of crap — Defeated. 3/4 waltz that degrades. Loop That Breaks."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_FINGER, GUITAR_DISTORTION, GUITAR_CLEAN,
                           DRUM_CHANNEL, CRASH)
from lib.drums import driving_emo, half_time, floor_tom_pulse
from lib.harmony import chord
from lib.melody import contour, broken_trail
from lib.bass import locked_bass
from lib.humanize import strum, humanize_velocity, SeededRng
from lib.directives import loop_that_breaks
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(15, "piece_of_crap", key="Am", tempo=120, time_sig=(3, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration  # 3 beats

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_FINGER)
    chords_inst = c.add_instrument("Chords", program=GUITAR_CLEAN)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    # Am natural minor
    chord_seq = [("A", "min"), ("C", "min"), ("G", "min"), ("E", "min")]

    # === Build 2-bar base loop ===
    loop_dur = 2 * bar

    # Base melody for loop
    base_mel = contour("Am", "natural_minor", direction="descending", num_notes=5,
                       octave=4, seed=c.seed, start_time=0.0,
                       note_duration=beat * 0.7, note_gap=beat * 0.2, velocity=80)

    # Generate 4 mutating repetitions
    loop_reps = loop_that_breaks(base_mel, repetitions=4, seed=c.seed)

    # === Section 1: 4 × 2-bar loops degrading ===
    for rep_idx, rep_notes in enumerate(loop_reps):
        time_offset = rep_idx * loop_dur

        # Drums get progressively sparse
        if rep_idx == 0:
            dr = driving_emo(bars=2, tempo=120, time_sig=(3, 4), seed=c.seed + rep_idx)
        elif rep_idx == 1:
            dr = half_time(bars=2, tempo=120, time_sig=(3, 4), seed=c.seed + rep_idx)
        elif rep_idx == 2:
            dr = floor_tom_pulse(bars=2, tempo=120, time_sig=(3, 4), seed=c.seed + rep_idx)
        else:
            # Very sparse - just one kick at the start
            dr = [pretty_midi.Note(velocity=70, pitch=36, start=0.0, end=0.1)]

        for n in dr:
            n.start += time_offset
            n.end += time_offset
        drums_inst.notes.extend(dr)

        # Place mutated melody notes
        for n in rep_notes:
            melody_inst.notes.append(pretty_midi.Note(
                velocity=max(1, min(127, n.velocity - rep_idx * 10)),
                pitch=max(0, min(127, n.pitch)),
                start=n.start + time_offset,
                end=n.end + time_offset,
            ))

        # Chords per loop, fading
        for ci in range(2):
            t = time_offset + ci * bar
            root, q = chord_seq[ci % 4]
            pitches = chord(root, q, octave=2, voicing="open")
            vel = max(30, 75 - rep_idx * 15)
            cn = [pretty_midi.Note(velocity=vel, pitch=p, start=t, end=t + bar * 0.85) for p in pitches]
            chords_inst.notes.extend(strum(cn, direction="down", spread_ms=30 + rep_idx * 10))

        # Bass fading
        bass_vel = max(30, 80 - rep_idx * 15)
        bass_inst.notes.append(pretty_midi.Note(velocity=bass_vel, pitch=33,
                               start=time_offset, end=time_offset + bar * 0.7))

    # === Section 2: 4 bars — drums gone, just chords + bass trailing off ===
    s2 = 4 * loop_dur

    for i in range(4):
        t = s2 + i * bar
        if t >= c.duration:
            break
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        vel = max(20, 50 - i * 8)
        cn = [pretty_midi.Note(velocity=vel, pitch=p, start=t,
                               end=min(t + bar * 0.9, c.duration)) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=50))

        bass_inst.notes.append(pretty_midi.Note(velocity=max(15, 45 - i * 10), pitch=33,
                               start=t, end=min(t + bar * 0.7, c.duration)))

    # Broken trail melody in section 2
    mel_s2 = contour("Am", "natural_minor", direction="descending", num_notes=8,
                     octave=4, seed=c.seed + 5, start_time=s2,
                     note_duration=beat * 0.6, note_gap=beat * 0.4, velocity=60)
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
