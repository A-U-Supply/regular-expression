#!/usr/bin/env python
"""Track 29: fuck you — Confrontational. Most song-like. Am Phrygian, 152bpm.
The Collapse. Clear verse/chorus feel: 4 bars verse → 4 bars chorus → collapse → final chorus."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_PICK, GUITAR_DISTORTION, GUITAR_OVERDRIVE,
                           DRUM_CHANNEL, CRASH, KICK)
from lib.drums import driving_emo, blast, no_snare
from lib.harmony import chord
from lib.melody import contour, spike, stutter
from lib.bass import locked_bass, driving_eighths
from lib.humanize import strum, humanize_velocity, SeededRng
from lib.directives import collapse_plan
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(29, "fuck_you", key="Am", tempo=152, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_PICK)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    # Am Phrygian: A Bb C D E F G
    verse_chord_seq = [("A", "min"), ("Bb", "min"), ("E", "min"), ("A", "min")]
    chorus_chord_seq = [("A", "min"), ("E", "min"), ("Bb", "min"), ("A", "min")]
    am_root = 33  # A1

    # === Verse: Bars 1-4 ===
    s_verse = 0.0
    de_verse = driving_emo(bars=4, tempo=152, time_sig=(4, 4), seed=c.seed)
    drums_inst.notes.extend(de_verse)

    kick_times_v = [i * bar + b * beat for i in range(4) for b in [0, 2]]
    bass_v = locked_bass(kick_times_v, root=am_root, fifth=40, bars=4,
                         tempo=152, seed=c.seed, velocity=95)
    bass_inst.notes.extend(bass_v)

    for i in range(4):
        t = i * bar
        root, q = verse_chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=85 + rng.randint(-5, 5), pitch=p,
                               start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=20))

    mel_verse = contour("Am", "phrygian", direction="descending", num_notes=12,
                        octave=4, seed=c.seed, start_time=s_verse,
                        note_duration=beat * 0.5, note_gap=beat * 0.15, velocity=90)
    melody_inst.notes.extend(mel_verse)

    # === Chorus: Bars 5-8 — Louder ===
    s_chorus = 4 * bar
    de_chorus = driving_emo(bars=4, tempo=152, time_sig=(4, 4), seed=c.seed + 1)
    for n in de_chorus:
        n.start += s_chorus
        n.end += s_chorus
        n.velocity = min(127, n.velocity + 15)
    drums_inst.notes.extend(de_chorus)

    kick_times_c = [s_chorus + i * bar + b * beat for i in range(4) for b in [0, 2]]
    bass_c = locked_bass(kick_times_c, root=am_root, fifth=40, bars=4,
                         tempo=152, seed=c.seed + 1, velocity=110)
    bass_inst.notes.extend(bass_c)

    for i in range(4):
        t = s_chorus + i * bar
        root, q = chorus_chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="closed")
        cn = [pretty_midi.Note(velocity=105, pitch=p, start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=15))

    mel_chorus = contour("Am", "phrygian", direction="ascending", num_notes=12,
                         octave=4, seed=c.seed + 1, start_time=s_chorus,
                         note_duration=beat * 0.45, note_gap=beat * 0.12, velocity=108)
    melody_inst.notes.extend(mel_chorus)

    # === Collapse: Bars 9-10 ===
    s_collapse = 8 * bar
    # Just one sustained bass note + floor tom
    bass_inst.notes.append(pretty_midi.Note(velocity=60, pitch=am_root,
                           start=s_collapse, end=s_collapse + 2 * bar))
    for beat_idx in range(8):  # 2 bars × 4 beats
        t_ft = s_collapse + beat_idx * beat
        drums_inst.notes.append(pretty_midi.Note(velocity=55 + rng.randint(-10, 10),
                                  pitch=43, start=t_ft, end=t_ft + 0.08))  # Floor tom

    # Spike at collapse
    spike_notes = spike(base_pitch=69, interval="min7", start=s_collapse, velocity=90)
    melody_inst.notes.extend(spike_notes)

    # === Final Chorus: Bars 11-14 — Maximum ===
    s_final = 10 * bar
    if s_final < c.duration:
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=CRASH,
                                start=s_final, end=s_final + 0.4))
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=KICK,
                                start=s_final, end=s_final + 0.1))

        bl_final = blast(bars=4, tempo=152, time_sig=(4, 4), seed=c.seed + 2)
        for n in bl_final:
            n.start += s_final
            n.end += s_final
            n.velocity = min(127, n.velocity + 20)
            if n.start < c.duration:
                drums_inst.notes.append(n)

        kick_times_f = [s_final + i * bar + b * beat for i in range(4) for b in [0, 2]]
        bass_f = locked_bass(kick_times_f, root=am_root, fifth=40, bars=4,
                             tempo=152, seed=c.seed + 2, velocity=125)
        for n in bass_f:
            if n.start < c.duration:
                bass_inst.notes.append(n)

        for i in range(4):
            t = s_final + i * bar
            if t >= c.duration:
                break
            root, q = chorus_chord_seq[i % 4]
            pitches = chord(root, q, octave=2, voicing="closed")
            cn = [pretty_midi.Note(velocity=120, pitch=p, start=t,
                                   end=min(t + bar * 0.9, c.duration)) for p in pitches]
            chords_inst.notes.extend(cn)

        mel_final = contour("Am", "phrygian", direction="ascending", num_notes=14,
                            octave=5, seed=c.seed + 3, start_time=s_final,
                            note_duration=beat * 0.4, note_gap=beat * 0.08, velocity=120)
        for n in mel_final:
            if n.start < c.duration:
                melody_inst.notes.append(n)

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
