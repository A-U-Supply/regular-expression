#!/usr/bin/env python
"""Track 33: this sucks — Sparse, resigned. A1 drone (33). Am natural minor, 3/4 waltz.
Fading melody. The Drone directive."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_FINGER, GUITAR_DISTORTION, PAD_WARM,
                           DRUM_CHANNEL, FLOOR_TOM, HAT_CLOSED)
from lib.drums import half_time, floor_tom_pulse
from lib.harmony import chord
from lib.melody import contour, phrase, broken_trail
from lib.bass import locked_bass
from lib.humanize import strum, SeededRng
from lib.directives import drone
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(33, "this_sucks", key="Am", tempo=100, time_sig=(3, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration  # 3 beats

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_FINGER)
    chords_inst = c.add_instrument("Chords", program=PAD_WARM)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)
    drone_inst = c.add_instrument("Drone", program=BASS_FINGER)

    # A1 drone (33) sustained entire track
    drone_note = drone(pitch=33, duration=c.duration, velocity=38)
    drone_inst.notes.append(drone_note)

    # Am natural minor
    chord_seq = [("A", "min"), ("C", "min"), ("G", "min"), ("E", "min")]
    am_root = 33  # A1

    total_bars = c.bars

    # === Section 1: Bars 1-3 — Drone alone (very sparse drums) ===
    # Just very soft hi-hat pulses
    for i in range(3):
        t = i * bar
        drums_inst.notes.append(pretty_midi.Note(velocity=30, pitch=HAT_CLOSED,
                                 start=t, end=t + 0.05))

    # === Section 2: Bars 4-7 — Waltz enters slowly ===
    s2 = 3 * bar
    ht = half_time(bars=4, tempo=100, time_sig=(3, 4), seed=c.seed)
    for n in ht:
        n.start += s2
        n.end += s2
        n.velocity = max(1, n.velocity - 35)  # Very quiet
    drums_inst.notes.extend(ht)

    # Bass: one note per bar, root
    for i in range(4):
        t = s2 + i * bar
        bass_inst.notes.append(pretty_midi.Note(velocity=55, pitch=am_root,
                               start=t, end=t + bar * 0.7))

    # Pad chords enter quietly
    for i in range(4):
        t = s2 + i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=1, voicing="open")
        vel = 35 + rng.randint(-5, 5)
        cn = [pretty_midi.Note(velocity=vel, pitch=p, start=t, end=t + bar * 0.9) for p in pitches]
        chords_inst.notes.extend(cn)

    # === Section 3: Bars 8-12 — Melody enters, then fades ===
    s3 = 7 * bar
    ft = floor_tom_pulse(bars=5, tempo=100, time_sig=(3, 4), seed=c.seed + 1)
    for n in ft:
        n.start += s3
        n.end += s3
        n.velocity = max(1, n.velocity - 25)
    drums_inst.notes.extend(ft)

    kick_times_s3 = [s3 + i * bar for i in range(5)]
    bass_s3 = locked_bass(kick_times_s3, root=am_root, fifth=40, bars=5, tempo=100,
                          seed=c.seed + 1, velocity=65)
    bass_inst.notes.extend(bass_s3)

    for i in range(5):
        t = s3 + i * bar
        if t >= c.duration:
            break
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        vel = max(25, 55 - i * 6)
        cn = [pretty_midi.Note(velocity=vel, pitch=p, start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=45))

    # Melody: ascending then broken trail
    mel_s3 = contour("Am", "natural_minor", direction="ascending", num_notes=10,
                     octave=4, seed=c.seed + 1, start_time=s3,
                     note_duration=beat * 0.8, note_gap=beat * 0.45, velocity=65)
    mel_broken = broken_trail(mel_s3, decay_point=5)
    for n in mel_broken:
        if n.start < c.duration:
            melody_inst.notes.append(n)

    # === Section 4: Final bars — just drone + one fading chord ===
    s4 = 12 * bar
    if s4 < c.duration:
        pitches = chord("A", "min", octave=1, voicing="open")
        for p in pitches:
            chords_inst.notes.append(pretty_midi.Note(velocity=20, pitch=p,
                                      start=s4, end=min(c.duration, s4 + 2 * bar)))

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
