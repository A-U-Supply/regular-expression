#!/usr/bin/env python
"""Track 20: fuck useless — Slow, heavy 6/8. A1 drone (33). Drone + sparse melody.
Feels futile. Am natural minor."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_FINGER, GUITAR_DISTORTION, GUITAR_CLEAN,
                           DRUM_CHANNEL, FLOOR_TOM, CRASH, KICK)
from lib.drums import half_time, floor_tom_pulse, driving_emo
from lib.harmony import chord
from lib.melody import contour, phrase, broken_trail
from lib.bass import locked_bass
from lib.humanize import strum, SeededRng
from lib.directives import drone
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(20, "fuck_useless", key="Am", tempo=100, time_sig=(6, 8), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration  # 6/8 bar

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_FINGER)
    chords_inst = c.add_instrument("Chords", program=GUITAR_CLEAN)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)
    drone_inst = c.add_instrument("Drone", program=BASS_FINGER)

    # A1 drone (33) sustained
    drone_note = drone(pitch=33, duration=c.duration, velocity=40)
    drone_inst.notes.append(drone_note)

    # Am natural minor chords
    chord_seq = [("A", "min"), ("C", "min"), ("G", "min"), ("D", "min")]

    # === Section 1: Bars 1-3 — Drone alone, then floor tom ===
    for i in range(2):
        t = (1 + i) * bar
        drums_inst.notes.append(pretty_midi.Note(velocity=65, pitch=FLOOR_TOM,
                                 start=t, end=t + 0.1))

    # === Section 2: Bars 4-8 — Bass + drums enter slowly ===
    s2 = 3 * bar
    ft = floor_tom_pulse(bars=5, tempo=100, time_sig=(6, 8), seed=c.seed)
    for n in ft:
        n.start += s2
        n.end += s2
        n.velocity = max(1, n.velocity - 15)
    drums_inst.notes.extend(ft)

    # Bass: slow sustained notes
    for i in range(5):
        t = s2 + i * bar
        bass_inst.notes.append(pretty_midi.Note(velocity=70, pitch=33,
                               start=t, end=t + bar * 0.8))

    # Sparse melody enters bar 6
    mel_s2 = phrase("Am", "natural_minor", bars=3, tempo=100, time_sig=(6, 8),
                    density=0.2, seed=c.seed, velocity=60)
    for n in mel_s2:
        melody_inst.notes.append(pretty_midi.Note(
            velocity=n.velocity, pitch=n.pitch,
            start=n.start + s2 + 2 * bar, end=n.end + s2 + 2 * bar + beat,
        ))

    # === Section 3: Bars 9-13 — Chords enter, heavier ===
    s3 = 8 * bar
    de = driving_emo(bars=5, tempo=100, time_sig=(6, 8), seed=c.seed + 1)
    for n in de:
        n.start += s3
        n.end += s3
    drums_inst.notes.extend(de)

    kick_times_s3 = [s3 + i * bar + b * beat for i in range(5) for b in [0, 2]]
    bass_s3 = locked_bass(kick_times_s3, root=33, fifth=40, bars=5, tempo=100,
                          seed=c.seed + 1, velocity=90)
    bass_inst.notes.extend(bass_s3)

    for i in range(5):
        t = s3 + i * bar
        if t >= c.duration:
            break
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=75 + rng.randint(-5, 5), pitch=p,
                               start=t, end=min(t + bar * 0.9, c.duration)) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=35))

    mel_s3 = contour("Am", "natural_minor", direction="descending", num_notes=12,
                     octave=4, seed=c.seed + 1, start_time=s3,
                     note_duration=beat * 0.9, note_gap=beat * 0.4, velocity=80)
    mel_s3_broken = broken_trail(mel_s3, decay_point=8)
    for n in mel_s3_broken:
        if n.start < c.duration:
            melody_inst.notes.append(n)

    # === Section 4: Final bar — just drone + one chord ===
    s4 = 13 * bar
    if s4 < c.duration:
        pitches = chord("A", "min", octave=1, voicing="open")
        for p in pitches:
            chords_inst.notes.append(pretty_midi.Note(velocity=35, pitch=p,
                                      start=s4, end=min(c.duration, s4 + 2 * bar)))

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
