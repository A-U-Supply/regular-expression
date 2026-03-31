#!/usr/bin/env python
"""Track 16: piece of junk — Hollowed out. E1 drone (28). Em Dorian. Sparse,
barely-there parts. Drone + slow sparse melody (Pad Warm) + fragments."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_FINGER, PAD_WARM, GUITAR_CLEAN,
                           DRUM_CHANNEL, FLOOR_TOM, HAT_CLOSED)
from lib.drums import half_time, floor_tom_pulse
from lib.harmony import chord
from lib.melody import phrase, contour, broken_trail
from lib.bass import locked_bass
from lib.humanize import strum, SeededRng
from lib.directives import drone
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(16, "piece_of_junk", key="Em", tempo=95, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_FINGER)
    chords_inst = c.add_instrument("Chords", program=GUITAR_CLEAN)
    melody_inst = c.add_instrument("Melody", program=PAD_WARM)
    drone_inst = c.add_instrument("Drone", program=BASS_FINGER)

    # E1 drone (28)
    drone_note = drone(pitch=28, duration=c.duration, velocity=38)
    drone_inst.notes.append(drone_note)

    # Em Dorian: E F# G A B C# D
    chord_seq = [("E", "min"), ("A", "min"), ("B", "min"), ("E", "min")]

    # === Section 1: Bars 1-4 — Drone alone, then very sparse drums enter ===
    # Bars 1-2: nothing but drone
    # Bars 3-4: one floor tom hit per bar
    for i in range(2):
        t = (2 + i) * bar
        drums_inst.notes.append(pretty_midi.Note(velocity=55, pitch=FLOOR_TOM,
                                 start=t, end=t + 0.1))
        drums_inst.notes.append(pretty_midi.Note(velocity=40, pitch=HAT_CLOSED,
                                 start=t + beat * 2, end=t + beat * 2 + 0.1))

    # === Section 2: Bars 5-8 — Sparse chords enter, very quiet ===
    s2 = 4 * bar
    for i in range(4):
        if rng.random() < 0.6:  # Not every bar
            t = s2 + i * bar
            root, q = chord_seq[i % 4]
            pitches = chord(root, q, octave=2, voicing="open")
            vel = 40 + rng.randint(-5, 5)
            cn = [pretty_midi.Note(velocity=vel, pitch=p,
                                   start=t + rng.uniform(0, beat),
                                   end=t + bar * 0.8) for p in pitches]
            chords_inst.notes.extend(strum(cn, direction="down", spread_ms=50))

    # Melody enters — Pad Warm, very slow, sparse
    mel_s2 = phrase("Em", "dorian", bars=4, tempo=95, time_sig=(4, 4),
                    density=0.25, seed=c.seed, velocity=55)
    for n in mel_s2:
        melody_inst.notes.append(pretty_midi.Note(
            velocity=n.velocity,
            pitch=n.pitch,
            start=n.start + s2,
            end=n.end + s2 + beat,  # Pad notes sustain longer
        ))

    # Bass: one long note per 2 bars
    bass_inst.notes.append(pretty_midi.Note(velocity=55, pitch=28,
                           start=s2, end=s2 + 2 * bar))
    bass_inst.notes.append(pretty_midi.Note(velocity=50, pitch=28,
                           start=s2 + 2 * bar, end=s2 + 4 * bar))

    # Sparse floor tom in section 2
    ft_s2 = floor_tom_pulse(bars=4, tempo=95, time_sig=(4, 4), seed=c.seed + 1)
    for n in ft_s2:
        n.start += s2
        n.end += s2
        n.velocity = max(1, n.velocity - 40)  # Very quiet
    drums_inst.notes.extend(ft_s2)

    # === Section 3: Bars 9-12 — Slightly fuller, bass joins with single notes ===
    s3 = 8 * bar
    ht = half_time(bars=4, tempo=95, time_sig=(4, 4), seed=c.seed + 2)
    for n in ht:
        n.start += s3
        n.end += s3
        n.velocity = max(1, n.velocity - 25)  # Quiet
    drums_inst.notes.extend(ht)

    for i in range(4):
        t = s3 + i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        vel = 55 + rng.randint(-5, 5)
        cn = [pretty_midi.Note(velocity=vel, pitch=p, start=t, end=t + bar * 0.9) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=40))

    # Bass: slow with slides
    kick_times_s3 = [s3 + i * bar for i in range(4)]
    bass_s3 = locked_bass(kick_times_s3, root=28, fifth=35, bars=4, tempo=95,
                          seed=c.seed + 2, velocity=60)
    bass_inst.notes.extend(bass_s3)

    mel_s3 = contour("Em", "dorian", direction="ascending", num_notes=8,
                     octave=4, seed=c.seed + 2, start_time=s3,
                     note_duration=beat * 2.0, note_gap=beat * 0.8, velocity=65)
    mel_broken = broken_trail(mel_s3, decay_point=5)
    for n in mel_broken:
        end_t = min(n.end + beat, c.duration)
        if end_t <= n.start:
            continue
        melody_inst.notes.append(pretty_midi.Note(
            velocity=n.velocity, pitch=n.pitch,
            start=n.start, end=end_t,
        ))

    # === Section 4: Fade — just drone and one chord ===
    s4 = 12 * bar
    if s4 < c.duration:
        pitches = chord("E", "min", octave=1, voicing="open")
        for p in pitches:
            chords_inst.notes.append(pretty_midi.Note(velocity=25, pitch=p,
                                      start=s4, end=min(c.duration, s4 + 2 * bar)))

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
