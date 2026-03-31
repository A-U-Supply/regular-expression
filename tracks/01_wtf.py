#!/usr/bin/env python
"""Track 01: wtf — The album opens mid-confusion. Rhythmic displacement makes
the melody feel persistently wrong against the rhythm section."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import BASS_PICK, GUITAR_DISTORTION, GUITAR_OVERDRIVE, DRUM_CHANNEL
from lib.drums import driving_emo, fill
from lib.harmony import chord, pedal_point
from lib.melody import contour, spike
from lib.bass import locked_bass, chromatic_approach
from lib.humanize import humanize_timing, humanize_velocity, strum, SeededRng
from lib.directives import rhythmic_displacement
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(1, "wtf", key="Em", tempo=138, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    # --- Instruments ---
    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_PICK)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    # --- E Phrygian: E F G A B C D ---
    # Progression: i - bII - v - i
    # Em - F - Bm - Em
    chord_sequence = [
        ("E", "min"),
        ("F", "min"),   # bII as minor for darker color
        ("B", "min"),
        ("E", "min"),
    ]

    # === Section 1: Bars 1-4 — Full band, everything locked ===
    drum_notes = driving_emo(bars=4, tempo=138, time_sig=(4, 4), seed=c.seed)
    drums_inst.notes.extend(drum_notes)

    kick_times = [i * bar + b * beat for i in range(4) for b in [0, 2]]
    bass_notes = locked_bass(kick_times, root=28, fifth=35, bars=4, tempo=138, seed=c.seed)
    bass_notes = humanize_velocity(bass_notes, spread=10, seed=c.seed)
    bass_inst.notes.extend(bass_notes)

    for i, (root, quality) in enumerate(chord_sequence):
        t = i * bar
        pitches = chord(root, quality, octave=2, voicing="open")
        chord_notes = [pretty_midi.Note(velocity=85 + rng.randint(-5, 5), pitch=p, start=t, end=t + bar * 0.9)
                       for p in pitches]
        chords_inst.notes.extend(strum(chord_notes, direction="down", spread_ms=25))

    mel_sec1 = contour("Em", "phrygian", direction="descending", num_notes=12,
                       octave=4, seed=c.seed, start_time=0.0, note_duration=beat * 0.8,
                       note_gap=beat * 0.2, velocity=90)
    melody_inst.notes.extend(mel_sec1)

    # === Section 2: Bars 5-8 — Melody displaced, chords go sus2 ===
    offset_sec2 = 4 * bar
    drum_notes_2 = driving_emo(bars=4, tempo=138, time_sig=(4, 4), seed=c.seed + 1)
    for n in drum_notes_2:
        n.start += offset_sec2
        n.end += offset_sec2
    drums_inst.notes.extend(drum_notes_2)

    kick_times_2 = [offset_sec2 + i * bar + b * beat for i in range(4) for b in [0, 2]]
    bass_notes_2 = locked_bass(kick_times_2, root=28, fifth=35, bars=4, tempo=138, seed=c.seed + 1)
    bass_inst.notes.extend(bass_notes_2)

    sus_chords = [("E", "sus2"), ("F", "sus2"), ("B", "sus2"), ("E", "sus2")]
    for i, (root, quality) in enumerate(sus_chords):
        t = offset_sec2 + i * bar
        pitches = chord(root, quality, octave=2, voicing="open")
        chord_notes = [pretty_midi.Note(velocity=80, pitch=p, start=t, end=t + bar * 0.9)
                       for p in pitches]
        chords_inst.notes.extend(strum(chord_notes, direction="down", spread_ms=25))

    mel_sec2 = contour("Em", "phrygian", direction="descending", num_notes=12,
                       octave=4, seed=c.seed + 2, start_time=offset_sec2,
                       note_duration=beat * 0.8, note_gap=beat * 0.2, velocity=85)
    mel_sec2_displaced = rhythmic_displacement(mel_sec2, offset_eighths=1, tempo=138)
    melody_inst.notes.extend(mel_sec2_displaced)

    # === Section 3: Bars 9-12 — Everything locks back in, louder ===
    offset_sec3 = 8 * bar
    drum_notes_3 = driving_emo(bars=4, tempo=138, time_sig=(4, 4), seed=c.seed + 3)
    for n in drum_notes_3:
        n.start += offset_sec3
        n.end += offset_sec3
        n.velocity = min(127, n.velocity + 15)
    drums_inst.notes.extend(drum_notes_3)

    kick_times_3 = [offset_sec3 + i * bar + b * beat for i in range(4) for b in [0, 2]]
    bass_notes_3 = locked_bass(kick_times_3, root=28, fifth=35, bars=4, tempo=138, seed=c.seed + 3,
                               velocity=115)
    bass_inst.notes.extend(bass_notes_3)

    for i, (root, quality) in enumerate(chord_sequence):
        t = offset_sec3 + i * bar
        pitches = chord(root, quality, octave=2, voicing="open")
        chord_notes = [pretty_midi.Note(velocity=105, pitch=p, start=t, end=t + bar * 0.9)
                       for p in pitches]
        chords_inst.notes.extend(strum(chord_notes, direction="down", spread_ms=20))

    # Melody with min7 spike at bar 9
    spike_notes = spike(base_pitch=64, interval="min7", start=offset_sec3, velocity=110)
    melody_inst.notes.extend(spike_notes)
    mel_sec3 = contour("Em", "phrygian", direction="descending", num_notes=10,
                       octave=4, seed=c.seed + 4, start_time=offset_sec3 + beat * 2,
                       note_duration=beat * 0.7, note_gap=beat * 0.3, velocity=100)
    melody_inst.notes.extend(mel_sec3)

    # === Section 4: Bars 13-14 — Sudden gap, one floor tom hit ===
    offset_sec4 = 12 * bar
    from lib.constants import FLOOR_TOM
    drums_inst.notes.append(pretty_midi.Note(velocity=110, pitch=FLOOR_TOM,
                                             start=offset_sec4 + bar, end=offset_sec4 + bar + 0.3))

    # === Section 5: Bars 15-16 — Crash back at max velocity ===
    offset_sec5 = 14 * bar
    if offset_sec5 < c.duration:
        from lib.constants import CRASH, KICK
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=CRASH,
                                                 start=offset_sec5, end=offset_sec5 + 0.5))
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=KICK,
                                                 start=offset_sec5, end=offset_sec5 + 0.1))
        remaining = c.duration - offset_sec5
        drum_notes_5 = driving_emo(bars=2, tempo=138, time_sig=(4, 4), seed=c.seed + 5)
        for n in drum_notes_5:
            n.start += offset_sec5
            n.end += offset_sec5
            n.velocity = min(127, n.velocity + 20)
            if n.start < c.duration:
                drums_inst.notes.append(n)

        for i, (root, quality) in enumerate(chord_sequence[:2]):
            t = offset_sec5 + i * bar
            if t < c.duration:
                pitches = chord(root, quality, octave=2, voicing="open")
                chord_notes = [pretty_midi.Note(velocity=120, pitch=p, start=t,
                               end=min(t + bar * 0.9, c.duration)) for p in pitches]
                chords_inst.notes.extend(chord_notes)

        bass_inst.notes.append(pretty_midi.Note(velocity=120, pitch=28,
                               start=offset_sec5, end=min(offset_sec5 + bar, c.duration)))

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
