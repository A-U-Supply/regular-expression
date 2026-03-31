#!/usr/bin/env python
"""Track 34: damn it — THE LAST TRACK. Starts moderate, strips away (Reverse Structure).
CRITICAL: Must end mid-phrase — melody cuts off unresolved, like giving up.
Em natural minor, 94bpm."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_FINGER, GUITAR_DISTORTION, GUITAR_CLEAN,
                           DRUM_CHANNEL, CRASH, KICK, FLOOR_TOM, HAT_CLOSED)
from lib.drums import driving_emo, half_time, floor_tom_pulse
from lib.harmony import chord
from lib.melody import contour, phrase, broken_trail
from lib.bass import locked_bass
from lib.humanize import strum, SeededRng
from lib.directives import reverse_structure_plan
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(34, "damn_it", key="Em", tempo=94, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_FINGER)
    chords_inst = c.add_instrument("Chords", program=GUITAR_CLEAN)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    # Em natural minor
    chord_seq = [("E", "min"), ("G", "min"), ("D", "min"), ("A", "min")]
    em_root = 28  # E1

    # === Section 1: Bars 1-4 — Full band, moderate intensity ===
    s1 = 0.0
    de_s1 = driving_emo(bars=4, tempo=94, time_sig=(4, 4), seed=c.seed)
    drums_inst.notes.extend(de_s1)

    kick_times_s1 = [i * bar + b * beat for i in range(4) for b in [0, 2]]
    bass_s1 = locked_bass(kick_times_s1, root=em_root, fifth=35, bars=4,
                          tempo=94, seed=c.seed, velocity=90)
    bass_inst.notes.extend(bass_s1)

    for i in range(4):
        t = i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=80 + rng.randint(-5, 5), pitch=p,
                               start=t, end=t + bar * 0.9) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=28))

    mel_s1 = contour("Em", "natural_minor", direction="descending", num_notes=12,
                     octave=4, seed=c.seed, start_time=s1,
                     note_duration=beat * 0.7, note_gap=beat * 0.3, velocity=85)
    melody_inst.notes.extend(mel_s1)

    # === Section 2: Bars 5-8 — Drums become half-time, start stripping ===
    s2 = 4 * bar
    ht_s2 = half_time(bars=4, tempo=94, time_sig=(4, 4), seed=c.seed + 1)
    for n in ht_s2:
        n.start += s2
        n.end += s2
    drums_inst.notes.extend(ht_s2)

    kick_times_s2 = [s2 + i * bar + b * beat for i in range(4) for b in [0, 2]]
    bass_s2 = locked_bass(kick_times_s2, root=em_root, fifth=35, bars=4,
                          tempo=94, seed=c.seed + 1, velocity=75)
    bass_inst.notes.extend(bass_s2)

    for i in range(4):
        t = s2 + i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=70, pitch=p, start=t, end=t + bar * 0.9) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=32))

    mel_s2 = contour("Em", "natural_minor", direction="ascending", num_notes=10,
                     octave=4, seed=c.seed + 1, start_time=s2,
                     note_duration=beat * 0.8, note_gap=beat * 0.35, velocity=75)
    melody_inst.notes.extend(mel_s2)

    # === Section 3: Bars 9-11 — Chords drop, just bass + sparse drums ===
    s3 = 8 * bar
    s3_bars = 3
    ft_s3 = floor_tom_pulse(bars=s3_bars, tempo=94, time_sig=(4, 4), seed=c.seed + 2)
    for n in ft_s3:
        n.start += s3
        n.end += s3
        n.velocity = max(1, n.velocity - 25)
    drums_inst.notes.extend(ft_s3)

    for i in range(s3_bars):
        t = s3 + i * bar
        bass_inst.notes.append(pretty_midi.Note(velocity=60, pitch=em_root,
                               start=t, end=t + bar * 0.7))

    # Melody fragment, broken trail
    mel_s3 = contour("Em", "natural_minor", direction="descending", num_notes=6,
                     octave=4, seed=c.seed + 2, start_time=s3,
                     note_duration=beat * 0.8, note_gap=beat * 0.4, velocity=60)
    mel_s3_broken = broken_trail(mel_s3, decay_point=3)
    melody_inst.notes.extend(mel_s3_broken)

    # === Section 4: Bars 12-13 — Drums gone, just bass ===
    s4 = 11 * bar
    s4_bars = 2

    for i in range(s4_bars):
        t = s4 + i * bar
        if t >= c.duration:
            break
        bass_inst.notes.append(pretty_midi.Note(velocity=max(30, 50 - i * 15), pitch=em_root,
                               start=t, end=min(t + bar * 0.7, c.duration)))

    # === CRITICAL FINAL SECTION: Melody cuts off unresolved ===
    # The last note starts but NEVER resolves — it is cut short before it would complete
    s_final = 13 * bar
    if s_final < c.duration:
        # A note that wants to be the E (tonic) but never gets there
        # Start a phrase at the penultimate note (F#4 or G4 — not the root)
        # The melody starts ascending toward resolution...
        unresolved_pitches = [62, 64, 67, 64, 62]  # D4, E4, G4, E4, D4 — not resolving to E
        mel_t = s_final
        for i, pitch in enumerate(unresolved_pitches):
            note_end = mel_t + beat * 0.9
            # Last note: cut it off before it naturally would end (unresolved)
            if i == len(unresolved_pitches) - 1:
                # This note STARTS but gets cut short — before resolution
                cutoff = min(mel_t + beat * 0.3, c.duration - 0.01)
                if mel_t < c.duration:
                    melody_inst.notes.append(pretty_midi.Note(
                        velocity=65, pitch=pitch,
                        start=mel_t, end=cutoff,  # Cut off mid-note, before resolving
                    ))
            else:
                if mel_t < c.duration:
                    melody_inst.notes.append(pretty_midi.Note(
                        velocity=65 - i * 5, pitch=pitch,
                        start=mel_t, end=min(note_end, c.duration),
                    ))
            mel_t += beat

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
