#!/usr/bin/env python
"""Track 05: shit — The descent begins. First of the sinking trilogy.
Heavy, deliberate. Establishes a motif that tracks 06 and 07 will degrade.
Drone on E1 sustains underneath everything."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


import pretty_midi
from lib.composer import Composer
from lib.constants import BASS_FINGER, GUITAR_DISTORTION, GUITAR_OVERDRIVE, DRUM_CHANNEL
from lib.drums import half_time, driving_emo, floor_tom_pulse
from lib.harmony import chord
from lib.melody import contour, broken_trail
from lib.bass import locked_bass
from lib.humanize import humanize_timing, humanize_velocity, strum, ghost_notes, SeededRng
from lib.directives import drone, collapse_plan
from lib.cli import parse_track_args
from lib.constants import CRASH, KICK, FLOOR_TOM


# === Shared motif for the sinking trilogy (tracks 05-07) ===
# Progression: i-III-VII-iv = Am-C-G-Dm
TRILOGY_CHORD_SEQ = [("A", "add9"), ("C", "add9"), ("G", "add9"), ("D", "add9")]
TRILOGY_ROOT = 33  # A1


def generate(seed=None):
    c = Composer(5, "shit", key="Am", tempo=108, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_FINGER)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)
    drone_inst = c.add_instrument("Drone", program=BASS_FINGER)

    # Drone: E1 (28) sustained entire track
    drone_note = drone(pitch=28, duration=c.duration, velocity=40)
    drone_inst.notes.append(drone_note)

    plan = collapse_plan(total_bars=15, collapse_bar=12, re_entry_bar=14)

    # === Section 1: Bars 1-4 — Half-time drums, chords only, establishing motif ===
    ht_notes = half_time(bars=4, tempo=108, time_sig=(4, 4), seed=c.seed)
    drums_inst.notes.extend(ht_notes)

    for bar_idx in range(4):
        t = bar_idx * bar
        root, quality = TRILOGY_CHORD_SEQ[bar_idx % 4]
        pitches = chord(root, quality, octave=2, voicing="open")
        chord_notes = [pretty_midi.Note(velocity=70 + rng.randint(-5, 5), pitch=p,
                       start=t, end=t + bar * 0.9) for p in pitches]
        chords_inst.notes.extend(strum(chord_notes, direction="down", spread_ms=30))

    # Bass: simple roots with ghost notes
    for bar_idx in range(4):
        t = bar_idx * bar
        root_pitches = [33, 36, 31, 38]  # A1, C2, G1, D2
        bass_note = pretty_midi.Note(velocity=80, pitch=root_pitches[bar_idx],
                                     start=t, end=t + bar * 0.7)
        bass_inst.notes.append(bass_note)

    # === Section 2: Bars 5-8 — Melody enters, floor tom pulse ===
    offset_s2 = 4 * bar

    ft_notes = floor_tom_pulse(bars=4, tempo=108, time_sig=(4, 4), seed=c.seed + 1)
    for n in ft_notes:
        n.start += offset_s2
        n.end += offset_s2
    drums_inst.notes.extend(ft_notes)

    for bar_idx in range(4):
        t = offset_s2 + bar_idx * bar
        root, quality = TRILOGY_CHORD_SEQ[bar_idx % 4]
        pitches = chord(root, quality, octave=2, voicing="open")
        chord_notes = [pretty_midi.Note(velocity=75, pitch=p,
                       start=t, end=t + bar * 0.9) for p in pitches]
        chords_inst.notes.extend(strum(chord_notes, direction="down", spread_ms=25))

    # Melody: A5 descending to E4
    mel_s2 = contour("Am", "natural_minor", direction="descending", num_notes=12,
                     octave=4, seed=c.seed + 1, start_time=offset_s2,
                     note_duration=beat * 1.2, note_gap=beat * 0.3, velocity=80)
    melody_inst.notes.extend(mel_s2)

    # Bass locks with floor tom
    ft_times = [offset_s2 + bar_idx * bar + b * beat for bar_idx in range(4) for b in [0, 2]]
    bass_s2 = locked_bass(ft_times, root=33, fifth=40, bars=4, tempo=108, seed=c.seed + 1, velocity=85)
    bass_s2_with_ghosts = ghost_notes(bass_s2, probability=0.4, vel_range=(20, 40), seed=c.seed + 1)
    bass_inst.notes.extend(bass_s2_with_ghosts)

    # === Section 3: Bars 9-12 — Full band driving emo, melody repeats higher ===
    offset_s3 = 8 * bar

    de_notes = driving_emo(bars=4, tempo=108, time_sig=(4, 4), seed=c.seed + 2)
    for n in de_notes:
        n.start += offset_s3
        n.end += offset_s3
    drums_inst.notes.extend(de_notes)

    for bar_idx in range(4):
        t = offset_s3 + bar_idx * bar
        root, quality = TRILOGY_CHORD_SEQ[bar_idx % 4]
        pitches = chord(root, quality, octave=2, voicing="open")
        chord_notes = [pretty_midi.Note(velocity=95 + rng.randint(-5, 5), pitch=p,
                       start=t, end=t + bar * 0.9) for p in pitches]
        chords_inst.notes.extend(strum(chord_notes, direction="down", spread_ms=20))

    # Melody repeats motif one octave higher
    mel_s3 = contour("Am", "natural_minor", direction="descending", num_notes=12,
                     octave=5, seed=c.seed + 1, start_time=offset_s3,
                     note_duration=beat * 1.2, note_gap=beat * 0.3, velocity=100)
    melody_inst.notes.extend(mel_s3)

    # Bass: driving with ghost notes
    kick_times_s3 = [offset_s3 + bar_idx * bar + b * beat for bar_idx in range(4) for b in [0, 2]]
    bass_s3 = locked_bass(kick_times_s3, root=33, fifth=40, bars=4, tempo=108,
                          seed=c.seed + 2, velocity=100)
    bass_s3_with_ghosts = ghost_notes(bass_s3, probability=0.5, vel_range=(20, 40), seed=c.seed + 2)
    bass_inst.notes.extend(bass_s3_with_ghosts)

    # === Section 4: Bars 13-14 — The Collapse: just bass, fragile ===
    offset_s4 = 12 * bar

    # Bass alone playing the motif roots, quiet
    for bar_idx in range(2):
        t = offset_s4 + bar_idx * bar
        root_pitches = [33, 36]  # A1, C2 (first two chords of motif)
        bass_inst.notes.append(pretty_midi.Note(velocity=45, pitch=root_pitches[bar_idx],
                               start=t, end=t + bar * 0.9))

    # === Section 5: Bar 15 — Everything crashes back fortissimo ===
    offset_s5 = 14 * bar
    if offset_s5 < c.duration:
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=CRASH,
                                start=offset_s5, end=offset_s5 + 0.4))
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=KICK,
                                start=offset_s5, end=offset_s5 + 0.1))

        # Full chord at max
        pitches = chord("A", "min", octave=2, voicing="open")
        for p in pitches:
            chords_inst.notes.append(pretty_midi.Note(velocity=120, pitch=p,
                                     start=offset_s5, end=min(offset_s5 + bar, c.duration)))

        bass_inst.notes.append(pretty_midi.Note(velocity=120, pitch=33,
                               start=offset_s5, end=min(offset_s5 + bar, c.duration)))

        melody_inst.notes.append(pretty_midi.Note(velocity=120, pitch=69,  # A4
                                 start=offset_s5, end=min(offset_s5 + bar, c.duration)))

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
