#!/usr/bin/env python
"""Track 27: fucking awful — Drone underneath, structure strips away from climax.
Em Phrygian, 105bpm. E1 drone (28) + Reverse Structure. Slow burn downward."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_FINGER, GUITAR_DISTORTION, GUITAR_CLEAN,
                           DRUM_CHANNEL, CRASH, KICK)
from lib.drums import driving_emo, half_time, floor_tom_pulse
from lib.harmony import chord
from lib.melody import contour, broken_trail, phrase
from lib.bass import locked_bass
from lib.humanize import strum, humanize_velocity, SeededRng
from lib.directives import drone, reverse_structure_plan
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(27, "fucking_awful", key="Em", tempo=105, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_FINGER)
    chords_inst = c.add_instrument("Chords", program=GUITAR_CLEAN)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)
    drone_inst = c.add_instrument("Drone", program=BASS_FINGER)

    # E1 drone (28) — sustained entire track
    drone_note = drone(pitch=28, duration=c.duration, velocity=38)
    drone_inst.notes.append(drone_note)

    # Em Phrygian: E F G A B C D
    chord_seq = [("E", "min"), ("F", "min"), ("B", "min"), ("E", "min")]
    em_root = 28  # E1

    # Reverse structure: 4 sections, each strips one layer
    # Section 1: all 4 instruments (bars 1-4)
    # Section 2: drop melody (bars 5-8)
    # Section 3: drop chords (bars 9-11)
    # Section 4: drop drums (bars 12-14)

    # === Section 1: Bars 1-4 — Full band ===
    s1 = 0.0
    de = driving_emo(bars=4, tempo=105, time_sig=(4, 4), seed=c.seed)
    for n in de:
        n.velocity = min(127, n.velocity + 10)
    drums_inst.notes.extend(de)

    kick_times = [i * bar + b * beat for i in range(4) for b in [0, 2]]
    bass_s1 = locked_bass(kick_times, root=em_root, fifth=35, bars=4,
                          tempo=105, seed=c.seed, velocity=100)
    bass_inst.notes.extend(bass_s1)

    for i in range(4):
        t = i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=90 + rng.randint(-5, 5), pitch=p,
                               start=t, end=t + bar * 0.9) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=25))

    mel_s1 = contour("Em", "phrygian", direction="descending", num_notes=14,
                     octave=5, seed=c.seed, start_time=s1,
                     note_duration=beat * 0.6, note_gap=beat * 0.2, velocity=100)
    melody_inst.notes.extend(mel_s1)

    # === Section 2: Bars 5-8 — Melody drops ===
    s2 = 4 * bar
    de_s2 = driving_emo(bars=4, tempo=105, time_sig=(4, 4), seed=c.seed + 1)
    for n in de_s2:
        n.start += s2
        n.end += s2
    drums_inst.notes.extend(de_s2)

    kick_times_s2 = [s2 + i * bar + b * beat for i in range(4) for b in [0, 2]]
    bass_s2 = locked_bass(kick_times_s2, root=em_root, fifth=35, bars=4,
                          tempo=105, seed=c.seed + 1, velocity=90)
    bass_inst.notes.extend(bass_s2)

    for i in range(4):
        t = s2 + i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=80, pitch=p, start=t, end=t + bar * 0.9) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=30))

    # === Section 3: Bars 9-11 — Chords drop too ===
    s3 = 8 * bar
    ht_s3 = half_time(bars=3, tempo=105, time_sig=(4, 4), seed=c.seed + 2)
    for n in ht_s3:
        n.start += s3
        n.end += s3
    drums_inst.notes.extend(ht_s3)

    kick_times_s3 = [s3 + i * bar + b * beat for i in range(3) for b in [0, 2]]
    bass_s3 = locked_bass(kick_times_s3, root=em_root, fifth=35, bars=3,
                          tempo=105, seed=c.seed + 2, velocity=75)
    bass_inst.notes.extend(bass_s3)

    # === Section 4: Bars 12-14 — Drums drop, just bass + drone ===
    s4 = 11 * bar
    s4_bars = max(1, int((c.duration - s4) / bar))

    for i in range(s4_bars):
        t = s4 + i * bar
        if t >= c.duration:
            break
        vel = max(25, 70 - i * 15)
        bass_inst.notes.append(pretty_midi.Note(velocity=vel, pitch=em_root,
                               start=t, end=min(t + bar * 0.8, c.duration)))

    # Final fading melody fragment
    if s4 < c.duration:
        mel_frag = phrase("Em", "phrygian", bars=s4_bars, tempo=105, time_sig=(4, 4),
                          density=0.15, seed=c.seed + 3, velocity=40)
        for n in mel_frag:
            t = n.start + s4
            if t < c.duration:
                melody_inst.notes.append(pretty_midi.Note(
                    velocity=n.velocity, pitch=n.pitch,
                    start=t, end=min(n.end + s4, c.duration),
                ))

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
