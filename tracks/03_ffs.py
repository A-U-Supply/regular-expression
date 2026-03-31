#!/usr/bin/env python
"""Track 03: ffs — Frustration boils over. Album's fastest tempo.
The Countdown: 8→4→2→1 bars, claustrophobic acceleration."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


import pretty_midi
from lib.composer import Composer
from lib.constants import BASS_PICK, GUITAR_DISTORTION, GUITAR_OVERDRIVE, DRUM_CHANNEL
from lib.drums import driving_emo, blast
from lib.harmony import chord, cluster
from lib.melody import contour, stutter, spike
from lib.bass import driving_eighths
from lib.humanize import humanize_timing, humanize_velocity, strum, SeededRng
from lib.directives import countdown_plan
from lib.cli import parse_track_args
from lib.constants import CRASH, KICK


def generate(seed=None):
    c = Composer(3, "ffs", key="Bm", tempo=160, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_PICK)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    plan = countdown_plan(tempo=160, time_sig=(4, 4), section_bars=[8, 4, 2, 1])
    # Progression: i-iv-v-i = Bm-Em-F#m-Bm
    chord_seq = [("B", "min"), ("E", "min"), ("F#", "min"), ("B", "min")]

    # === Section 1: 8 bars — driving emo + clusters ===
    s1_start, s1_end = plan["bar_boundaries"][0]
    s1_offset = s1_start * bar

    drum_s1 = driving_emo(bars=8, tempo=160, time_sig=(4, 4), seed=c.seed)
    for n in drum_s1:
        n.start += s1_offset
        n.end += s1_offset
    drums_inst.notes.extend(drum_s1)

    bass_s1 = driving_eighths(root=35, bars=8, tempo=160)  # B1
    bass_s1 = humanize_timing(bass_s1, spread_ms=5, seed=c.seed)
    bass_s1 = humanize_velocity(bass_s1, spread=12, seed=c.seed)
    for n in bass_s1:
        n.start += s1_offset
        n.end += s1_offset
    bass_inst.notes.extend(bass_s1)

    for bar_idx in range(8):
        t = s1_offset + bar_idx * bar
        root, quality = chord_seq[bar_idx % 4]
        pitches = chord(root, quality, octave=2, voicing="open")
        chord_notes = [pretty_midi.Note(velocity=90 + rng.randint(-5, 5), pitch=p,
                       start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(chord_notes, direction="down", spread_ms=20))

        # Cluster on chord changes (every other bar for variety)
        if bar_idx % 2 == 0:
            cluster_pitches = cluster(pitches[0] + 12, width=2)
            for cp in cluster_pitches:
                chords_inst.notes.append(pretty_midi.Note(
                    velocity=rng.randint(60, 80), pitch=cp,
                    start=t, end=t + beat * 0.5))

    mel_s1 = contour("Bm", "natural_minor", direction="descending", num_notes=20,
                     octave=4, seed=c.seed, start_time=s1_offset,
                     note_duration=beat * 0.7, note_gap=beat * 0.3, velocity=95)
    melody_inst.notes.extend(mel_s1)

    # === Section 2: 4 bars — power chords, same riff stripped down ===
    s2_start, s2_end = plan["bar_boundaries"][1]
    s2_offset = s2_start * bar

    drum_s2 = driving_emo(bars=4, tempo=160, time_sig=(4, 4), seed=c.seed + 1)
    for n in drum_s2:
        n.start += s2_offset
        n.end += s2_offset
        n.velocity = min(127, n.velocity + 10)
    drums_inst.notes.extend(drum_s2)

    bass_s2 = driving_eighths(root=35, bars=4, tempo=160, velocity=115)
    for n in bass_s2:
        n.start += s2_offset
        n.end += s2_offset
    bass_inst.notes.extend(bass_s2)

    for bar_idx in range(4):
        t = s2_offset + bar_idx * bar
        root, _ = chord_seq[bar_idx % 4]
        pitches = chord(root, "power", octave=2)
        for p in pitches:
            chords_inst.notes.append(pretty_midi.Note(velocity=110, pitch=p,
                                     start=t, end=t + bar * 0.9))

    mel_s2 = contour("Bm", "natural_minor", direction="descending", num_notes=10,
                     octave=4, seed=c.seed + 2, start_time=s2_offset,
                     note_duration=beat * 0.6, note_gap=beat * 0.4, velocity=105)
    melody_inst.notes.extend(mel_s2)

    # === Section 3: 2 bars — blast beat + melody spikes ===
    s3_start, s3_end = plan["bar_boundaries"][2]
    s3_offset = s3_start * bar

    blast_notes = blast(bars=2, tempo=160, time_sig=(4, 4), seed=c.seed + 2)
    for n in blast_notes:
        n.start += s3_offset
        n.end += s3_offset
    drums_inst.notes.extend(blast_notes)

    bass_s3 = driving_eighths(root=35, bars=2, tempo=160, velocity=120)
    for n in bass_s3:
        n.start += s3_offset
        n.end += s3_offset
    bass_inst.notes.extend(bass_s3)

    # Melody spikes
    for i in range(4):
        sp = spike(base_pitch=71, interval="min7", start=s3_offset + i * beat * 2, velocity=115)
        melody_inst.notes.extend(sp)

    # Power chords
    pitches = chord("B", "power", octave=2)
    for p in pitches:
        chords_inst.notes.append(pretty_midi.Note(velocity=120, pitch=p,
                                 start=s3_offset, end=s3_offset + 2 * bar))

    # === Section 4: 1 bar — unison B2, max velocity ===
    s4_start, s4_end = plan["bar_boundaries"][3]
    s4_offset = s4_start * bar

    # All instruments on B2 (47) and B1 (35)
    drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=CRASH,
                            start=s4_offset, end=s4_offset + 0.3))
    drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=KICK,
                            start=s4_offset, end=s4_offset + 0.1))

    unison_pitches = [35, 47, 59, 71]  # B across octaves
    for p in unison_pitches:
        for inst in [bass_inst, chords_inst, melody_inst]:
            inst.notes.append(pretty_midi.Note(velocity=127, pitch=p,
                              start=s4_offset, end=s4_offset + bar * 0.9))

    # Half-bar silence at the end (no notes needed — just don't add any)

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
