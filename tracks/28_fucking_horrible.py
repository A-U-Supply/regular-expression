#!/usr/bin/env python
"""Track 28: fucking horrible — Two contrasting sections welded with noise.
Bm natural minor → F#m Phrygian at midpoint. Two Songs Stitched."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_PICK, GUITAR_DISTORTION, GUITAR_OVERDRIVE,
                           DRUM_CHANNEL, CRASH, KICK, FLOOR_TOM)
from lib.drums import driving_emo, blast, half_time
from lib.harmony import chord, cluster
from lib.melody import contour, spike, stutter
from lib.bass import locked_bass, driving_eighths
from lib.humanize import strum, humanize_velocity, SeededRng
from lib.directives import two_songs_stitched_plan
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(28, "fucking_horrible", key="Bm", tempo=140, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_PICK)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    total_bars = c.bars
    split_bar = total_bars // 2  # Midpoint
    plan = two_songs_stitched_plan(total_bars=total_bars, split_bar=split_bar, transition_bars=1)

    # === Song A: Bm natural minor ===
    song_a_bars = plan["song_a"][1]
    bm_chord_seq = [("B", "min"), ("D", "min"), ("A", "min"), ("E", "min")]
    bm_root = 35  # B1

    de_a = driving_emo(bars=song_a_bars, tempo=140, time_sig=(4, 4), seed=c.seed)
    drums_inst.notes.extend(de_a)

    kick_times_a = [i * bar + b * beat for i in range(song_a_bars) for b in [0, 2]]
    bass_a = locked_bass(kick_times_a, root=bm_root, fifth=42, bars=song_a_bars,
                         tempo=140, seed=c.seed, velocity=105)
    bass_inst.notes.extend(bass_a)

    for i in range(song_a_bars):
        t = i * bar
        root, q = bm_chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=90 + rng.randint(-5, 5), pitch=p,
                               start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=20))

    mel_a = contour("Bm", "natural_minor", direction="descending", num_notes=song_a_bars * 3,
                    octave=4, seed=c.seed, start_time=0.0,
                    note_duration=beat * 0.5, note_gap=beat * 0.15, velocity=95)
    melody_inst.notes.extend(mel_a)

    # === Transition: 1 bar — Noise cluster ===
    t_trans = split_bar * bar
    cluster_pitches = cluster(center_pitch=47, width=3)
    for cp in cluster_pitches:
        chords_inst.notes.append(pretty_midi.Note(velocity=115, pitch=cp,
                                  start=t_trans, end=t_trans + beat * 0.4))

    drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=CRASH,
                             start=t_trans, end=t_trans + 0.4))

    # Stutter fill at transition
    stut = stutter(pitch=59, count=6, note_duration=beat * 0.12, gap=0.02,
                   start=t_trans + beat * 0.5, velocity=110)
    melody_inst.notes.extend(stut)

    # Floor tom roll
    for sub in range(6):
        t_roll = t_trans + sub * beat * 0.15
        drums_inst.notes.append(pretty_midi.Note(velocity=85 + rng.randint(-10, 10),
                                  pitch=FLOOR_TOM, start=t_roll, end=t_roll + 0.1))

    # === Song B: F#m Phrygian ===
    s_b_start_bar = plan["song_b"][0]
    s_b_start = s_b_start_bar * bar
    s_b_bars = plan["song_b"][1] - s_b_start_bar

    fs_chord_seq = [("F#", "min"), ("G", "min"), ("C#", "min"), ("F#", "min")]
    fs_root = 30  # F#1

    # Song B is heavier — blast beats
    bl_b = blast(bars=min(s_b_bars, 4), tempo=140, time_sig=(4, 4), seed=c.seed + 1)
    for n in bl_b:
        n.start += s_b_start
        n.end += s_b_start
        n.velocity = min(127, n.velocity + 15)
    drums_inst.notes.extend(bl_b)

    if s_b_bars > 4:
        de_b_extra = driving_emo(bars=s_b_bars - 4, tempo=140, time_sig=(4, 4), seed=c.seed + 11)
        for n in de_b_extra:
            n.start += s_b_start + 4 * bar
            n.end += s_b_start + 4 * bar
        drums_inst.notes.extend(de_b_extra)

    kick_times_b = [s_b_start + i * bar + b * beat for i in range(s_b_bars) for b in [0, 2]]
    bass_b = locked_bass(kick_times_b, root=fs_root, fifth=37, bars=s_b_bars,
                         tempo=140, seed=c.seed + 1, velocity=115)
    for n in bass_b:
        if n.start < c.duration:
            bass_inst.notes.append(n)

    for i in range(s_b_bars):
        t = s_b_start + i * bar
        if t >= c.duration:
            break
        root, q = fs_chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="closed")
        cn = [pretty_midi.Note(velocity=110, pitch=p, start=t,
                               end=min(t + bar * 0.85, c.duration)) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=12))

    mel_b = contour("F#m", "phrygian", direction="ascending", num_notes=s_b_bars * 3,
                    octave=4, seed=c.seed + 2, start_time=s_b_start,
                    note_duration=beat * 0.4, note_gap=beat * 0.1, velocity=112)
    for n in mel_b:
        if n.start < c.duration:
            melody_inst.notes.append(n)

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
