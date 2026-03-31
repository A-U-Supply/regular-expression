#!/usr/bin/env python
"""Track 24: fucking broken — Furious, then breaks. Dm natural minor, 148bpm.
The Collapse: collapse to bass alone, then re-entry."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_PICK, GUITAR_DISTORTION, GUITAR_OVERDRIVE,
                           DRUM_CHANNEL, CRASH, KICK)
from lib.drums import blast, driving_emo, no_snare
from lib.harmony import chord, cluster
from lib.melody import contour, spike, stutter
from lib.bass import locked_bass, driving_eighths, counter_melody
from lib.humanize import strum, humanize_velocity, SeededRng
from lib.directives import collapse_plan
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(24, "fucking_broken", key="Dm", tempo=148, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_PICK)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    # Dm natural minor
    chord_seq = [("D", "min"), ("F", "min"), ("C", "min"), ("G", "min")]
    dm_root = 38  # D2

    total_bars = c.bars
    plan = collapse_plan(total_bars=total_bars, collapse_bar=9, re_entry_bar=12)

    # === Before collapse: Bars 1-9 — Furious ===
    pre_bars = plan["before"][1]  # 9

    bl = blast(bars=4, tempo=148, time_sig=(4, 4), seed=c.seed)
    for n in bl:
        n.velocity = min(127, n.velocity + 15)
    drums_inst.notes.extend(bl)

    de = driving_emo(bars=5, tempo=148, time_sig=(4, 4), seed=c.seed + 1)
    for n in de:
        n.start += 4 * bar
        n.end += 4 * bar
        n.velocity = min(127, n.velocity + 15)
    drums_inst.notes.extend(de)

    kick_times = [i * bar + b * beat for i in range(pre_bars) for b in [0, 2]]
    bass_pre = locked_bass(kick_times, root=dm_root, fifth=45, bars=pre_bars,
                           tempo=148, seed=c.seed, velocity=115)
    bass_inst.notes.extend(bass_pre)

    for i in range(pre_bars):
        t = i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="closed")
        cn = [pretty_midi.Note(velocity=105 + rng.randint(-5, 5), pitch=p,
                               start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=12))

    mel_pre = contour("Dm", "natural_minor", direction="descending", num_notes=pre_bars * 3,
                      octave=4, seed=c.seed, start_time=0.0,
                      note_duration=beat * 0.4, note_gap=beat * 0.1, velocity=110)
    melody_inst.notes.extend(mel_pre)

    # === Collapse: Bars 10-12 — Bass alone ===
    s_solo = plan["solo"][0] * bar
    solo_bars = plan["solo"][1] - plan["solo"][0]

    cm_bass = counter_melody("Dm", "natural_minor", bars=solo_bars, tempo=148,
                             time_sig=(4, 4), seed=c.seed + 2, velocity=70)
    for n in cm_bass:
        bass_inst.notes.append(pretty_midi.Note(
            velocity=n.velocity, pitch=n.pitch,
            start=n.start + s_solo, end=n.end + s_solo,
        ))

    # === Re-entry: Bars 13-end ===
    s_re = plan["after"][0] * bar
    if s_re < c.duration:
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=CRASH,
                                start=s_re, end=s_re + 0.4))
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=KICK,
                                start=s_re, end=s_re + 0.1))

        re_bars = int((c.duration - s_re) / bar)
        bl_re = blast(bars=re_bars, tempo=148, time_sig=(4, 4), seed=c.seed + 3)
        for n in bl_re:
            n.start += s_re
            n.end += s_re
            n.velocity = min(127, n.velocity + 20)
            if n.start < c.duration:
                drums_inst.notes.append(n)

        kick_times_re = [s_re + i * bar + b * beat for i in range(re_bars) for b in [0, 2]]
        bass_re = locked_bass(kick_times_re, root=dm_root, fifth=45, bars=re_bars,
                              tempo=148, seed=c.seed + 3, velocity=125)
        for n in bass_re:
            if n.start < c.duration:
                bass_inst.notes.append(n)

        for i in range(re_bars):
            t = s_re + i * bar
            if t >= c.duration:
                break
            pitches = chord("D", "min", octave=2, voicing="closed")
            cn = [pretty_midi.Note(velocity=120, pitch=p, start=t,
                                   end=min(t + bar * 0.9, c.duration)) for p in pitches]
            chords_inst.notes.extend(cn)

        # Cluster hit at re-entry
        cluster_pitches = cluster(center_pitch=62, width=2)
        for cp in cluster_pitches:
            chords_inst.notes.append(pretty_midi.Note(velocity=115, pitch=cp,
                                      start=s_re, end=s_re + beat * 0.4))

        mel_re = contour("Dm", "natural_minor", direction="ascending", num_notes=re_bars * 3,
                         octave=4, seed=c.seed + 4, start_time=s_re,
                         note_duration=beat * 0.4, note_gap=beat * 0.08, velocity=118)
        for n in mel_re:
            if n.start < c.duration:
                melody_inst.notes.append(n)

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
