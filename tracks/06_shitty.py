#!/usr/bin/env python
"""Track 06: shitty — Sinking trilogy pt 2. Same motif as 05 but heavier,
slower. Dorian mode, displaced bass. Everything drags."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import BASS_FINGER, GUITAR_DISTORTION, GUITAR_OVERDRIVE, DRUM_CHANNEL, FLOOR_TOM
from lib.drums import half_time, driving_emo, floor_tom_pulse
from lib.harmony import chord
from lib.melody import contour
from lib.bass import locked_bass
from lib.humanize import humanize_velocity, strum, ghost_notes, SeededRng
from lib.directives import rhythmic_displacement, drone
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(6, "shitty", key="Am", tempo=98, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_FINGER)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    # Dorian versions of the trilogy chords (same roots, dorian color)
    dorian_chords = [("A", "min"), ("C", "min"), ("G", "min"), ("D", "min")]

    # === Section 1: Bars 1-4 — Half-time, chords only ===
    ht = half_time(bars=4, tempo=98, time_sig=(4, 4), seed=c.seed)
    drums_inst.notes.extend(ht)

    for i in range(4):
        t = i * bar
        root, quality = dorian_chords[i % 4]
        pitches = chord(root, quality, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=65, pitch=p, start=t, end=t + bar * 0.9) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=30))

    # === Section 2: Bars 5-8 — Melody enters, same contour as 05 but lower ===
    s2 = 4 * bar
    ht2 = half_time(bars=4, tempo=98, time_sig=(4, 4), seed=c.seed + 1)
    for n in ht2:
        n.start += s2; n.end += s2
    drums_inst.notes.extend(ht2)

    for i in range(4):
        t = s2 + i * bar
        root, quality = dorian_chords[i % 4]
        pitches = chord(root, quality, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=70, pitch=p, start=t, end=t + bar * 0.9) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=25))

    mel = contour("Am", "dorian", direction="descending", num_notes=10, octave=3,
                  seed=c.seed, start_time=s2, note_duration=beat * 1.5,
                  note_gap=beat * 0.5, velocity=75)
    melody_inst.notes.extend(mel)

    # Bass: simple roots
    for i in range(4):
        t = s2 + i * bar
        bass_inst.notes.append(pretty_midi.Note(velocity=80, pitch=[33, 36, 31, 38][i],
                               start=t, end=t + bar * 0.7))

    # === Section 3: Bars 9-12 — Full band, bass displaced ===
    s3 = 8 * bar
    de = driving_emo(bars=4, tempo=98, time_sig=(4, 4), seed=c.seed + 2)
    for n in de:
        n.start += s3; n.end += s3
    drums_inst.notes.extend(de)

    for i in range(4):
        t = s3 + i * bar
        root, quality = dorian_chords[i % 4]
        pitches = chord(root, quality, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=85, pitch=p, start=t, end=t + bar * 0.9) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=20))

    mel2 = contour("Am", "dorian", direction="descending", num_notes=12, octave=4,
                   seed=c.seed + 1, start_time=s3, note_duration=beat * 1.2,
                   note_gap=beat * 0.3, velocity=90)
    melody_inst.notes.extend(mel2)

    # Displaced bass
    kick_times = [s3 + i * bar + b * beat for i in range(4) for b in [0, 2]]
    bass_s3 = locked_bass(kick_times, root=33, fifth=40, bars=4, tempo=98, seed=c.seed + 2, velocity=95)
    bass_s3 = rhythmic_displacement(bass_s3, offset_eighths=1, tempo=98)
    bass_s3 = ghost_notes(bass_s3, probability=0.4, vel_range=(20, 40), seed=c.seed + 2)
    bass_inst.notes.extend(bass_s3)

    # === Section 4: Bars 13-14 — Just displaced bass + floor tom ===
    s4 = 12 * bar
    ft = floor_tom_pulse(bars=2, tempo=98, time_sig=(4, 4), seed=c.seed + 3)
    for n in ft:
        n.start += s4; n.end += s4
    drums_inst.notes.extend(ft)

    bass_end_t = min(s4 + 2 * bar, c.duration - 0.01)
    bass_end = [pretty_midi.Note(velocity=60, pitch=33, start=s4, end=s4 + bar),
                pretty_midi.Note(velocity=50, pitch=33, start=s4 + bar, end=max(s4 + bar + 0.01, bass_end_t))]
    bass_end = rhythmic_displacement(bass_end, offset_eighths=1, tempo=98)
    bass_inst.notes.extend(bass_end)

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
