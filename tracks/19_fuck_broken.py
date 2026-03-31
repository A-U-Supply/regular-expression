#!/usr/bin/env python
"""Track 19: fuck broken — Brutal center begins. Two riffs welded together.
Dm Phrygian → Am at ~15s mark. Two Songs Stitched."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_PICK, GUITAR_DISTORTION, GUITAR_OVERDRIVE,
                           DRUM_CHANNEL, CRASH, KICK, SNARE, FLOOR_TOM)
from lib.drums import driving_emo, blast, no_snare
from lib.harmony import chord, cluster
from lib.melody import contour, spike, stutter
from lib.bass import locked_bass, driving_eighths
from lib.humanize import strum, humanize_velocity, SeededRng
from lib.directives import two_songs_stitched_plan
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(19, "fuck_broken", key="Dm", tempo=142, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_PICK)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    # Two Songs Stitched: split at bar ~8 (~15s at 142bpm)
    total_bars = c.bars
    split_bar = int(15.0 / bar)  # ~bar 8
    plan = two_songs_stitched_plan(total_bars=total_bars, split_bar=split_bar, transition_bars=1)

    # === Song A: Dm Phrygian ===
    song_a_bars = plan["song_a"][1]  # bars 0..split_bar
    dm_chord_seq = [("D", "min"), ("Eb", "min"), ("A", "min"), ("D", "min")]

    de_a = blast(bars=song_a_bars, tempo=142, time_sig=(4, 4), seed=c.seed)
    drums_inst.notes.extend(de_a)

    kick_times_a = [i * bar + b * beat for i in range(song_a_bars) for b in [0, 2]]
    bass_a = locked_bass(kick_times_a, root=38, fifth=45, bars=song_a_bars,
                         tempo=142, seed=c.seed, velocity=110)
    bass_inst.notes.extend(bass_a)

    for i in range(song_a_bars):
        t = i * bar
        root, q = dm_chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="closed")
        cn = [pretty_midi.Note(velocity=100 + rng.randint(-5, 5), pitch=p,
                               start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=15))

    mel_a = contour("Dm", "phrygian", direction="descending", num_notes=song_a_bars * 3,
                    octave=4, seed=c.seed, start_time=0.0,
                    note_duration=beat * 0.4, note_gap=beat * 0.1, velocity=105)
    melody_inst.notes.extend(mel_a)

    # === Transition: 1 bar of noise/cluster ===
    t_trans = split_bar * bar
    cluster_pitches = cluster(center_pitch=38, width=3)
    for cp in cluster_pitches:
        chords_inst.notes.append(pretty_midi.Note(velocity=110, pitch=cp,
                                  start=t_trans, end=t_trans + beat * 0.5))
    drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=CRASH,
                             start=t_trans, end=t_trans + 0.4))
    # Floor tom roll in transition
    for sub in range(8):
        t_roll = t_trans + sub * beat * 0.125
        drums_inst.notes.append(pretty_midi.Note(velocity=90 + rng.randint(-10, 10),
                                  pitch=FLOOR_TOM, start=t_roll, end=t_roll + 0.08))

    # === Song B: Am natural minor ===
    s_b_start = plan["song_b"][0] * bar
    s_b_end_bar = plan["song_b"][1]
    s_b_bars = s_b_end_bar - plan["song_b"][0]

    am_chord_seq = [("A", "min"), ("C", "min"), ("G", "min"), ("E", "min")]

    de_b = driving_emo(bars=s_b_bars, tempo=142, time_sig=(4, 4), seed=c.seed + 1)
    for n in de_b:
        n.start += s_b_start
        n.end += s_b_start
        n.velocity = min(127, n.velocity + 10)
    drums_inst.notes.extend(de_b)

    kick_times_b = [s_b_start + i * bar + b * beat for i in range(s_b_bars) for b in [0, 2]]
    bass_b = locked_bass(kick_times_b, root=33, fifth=40, bars=s_b_bars,
                         tempo=142, seed=c.seed + 1, velocity=115)
    for n in bass_b:
        if n.start < c.duration:
            bass_inst.notes.append(n)

    for i in range(s_b_bars):
        t = s_b_start + i * bar
        if t >= c.duration:
            break
        root, q = am_chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="closed")
        cn = [pretty_midi.Note(velocity=110, pitch=p, start=t,
                               end=min(t + bar * 0.85, c.duration)) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=12))

    mel_b = contour("Am", "natural_minor", direction="ascending", num_notes=s_b_bars * 3,
                    octave=4, seed=c.seed + 2, start_time=s_b_start,
                    note_duration=beat * 0.4, note_gap=beat * 0.1, velocity=110)
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
