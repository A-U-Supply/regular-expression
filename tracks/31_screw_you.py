#!/usr/bin/env python
"""Track 31: screw you — Direct confrontation. Dm Phrygian, 145bpm.
Unison collapse near the end, then explosive finish. Unison Collapse."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_PICK, GUITAR_DISTORTION, GUITAR_OVERDRIVE,
                           DRUM_CHANNEL, CRASH, KICK)
from lib.drums import driving_emo, blast
from lib.harmony import chord, cluster
from lib.melody import contour, spike, stutter
from lib.bass import locked_bass, driving_eighths
from lib.humanize import strum, humanize_velocity, SeededRng
from lib.directives import unison_collapse
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(31, "screw_you", key="Dm", tempo=145, time_sig=(4, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_PICK)
    chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    # Dm Phrygian: D Eb F G A Bb C
    chord_seq = [("D", "min"), ("Eb", "min"), ("A", "min"), ("D", "min")]
    dm_root = 38  # D2

    total_bars = c.bars
    collapse_bar = total_bars - 4
    finish_bar = total_bars - 2

    # === Section 1: Before collapse — full band driving ===
    pre_bars = collapse_bar

    de = driving_emo(bars=pre_bars, tempo=145, time_sig=(4, 4), seed=c.seed)
    for n in de:
        n.velocity = min(127, n.velocity + 10)
    drums_inst.notes.extend(de)

    kick_times = [i * bar + b * beat for i in range(pre_bars) for b in [0, 2]]
    bass_pre = locked_bass(kick_times, root=dm_root, fifth=45, bars=pre_bars,
                           tempo=145, seed=c.seed, velocity=110)
    bass_inst.notes.extend(bass_pre)

    for i in range(pre_bars):
        t = i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=95 + rng.randint(-5, 5), pitch=p,
                               start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=18))

    # Melody in two passes
    half_pre = pre_bars // 2
    mel_pre1 = contour("Dm", "phrygian", direction="descending", num_notes=half_pre * 3,
                       octave=4, seed=c.seed, start_time=0.0,
                       note_duration=beat * 0.5, note_gap=beat * 0.15, velocity=100)
    melody_inst.notes.extend(mel_pre1)

    mel_pre2 = contour("Dm", "phrygian", direction="ascending", num_notes=half_pre * 3,
                       octave=4, seed=c.seed + 1, start_time=half_pre * bar,
                       note_duration=beat * 0.45, note_gap=beat * 0.12, velocity=108)
    melody_inst.notes.extend(mel_pre2)

    # === Unison Collapse: D for 2 bars ===
    s_collapse = collapse_bar * bar
    collapse_dur = (finish_bar - collapse_bar) * bar

    # D at multiple octaves
    bass_inst.notes.append(pretty_midi.Note(velocity=110, pitch=26,  # D1
                           start=s_collapse, end=s_collapse + collapse_dur))
    chords_inst.notes.append(pretty_midi.Note(velocity=110, pitch=38,  # D2
                              start=s_collapse, end=s_collapse + collapse_dur))
    melody_inst.notes.append(pretty_midi.Note(velocity=110, pitch=62,  # D4
                              start=s_collapse, end=s_collapse + collapse_dur))

    # Drum stops during unison except for kick
    for beat_idx in range(int(collapse_dur / beat)):
        if beat_idx % 4 == 0:
            drums_inst.notes.append(pretty_midi.Note(velocity=100, pitch=KICK,
                                     start=s_collapse + beat_idx * beat,
                                     end=s_collapse + beat_idx * beat + 0.1))

    # === Explosive finish: Final 2 bars ===
    s_finish = finish_bar * bar
    if s_finish < c.duration:
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=CRASH,
                                start=s_finish, end=s_finish + 0.4))
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=KICK,
                                start=s_finish, end=s_finish + 0.1))

        finish_bars = int((c.duration - s_finish) / bar)
        bl = blast(bars=max(1, finish_bars), tempo=145, time_sig=(4, 4), seed=c.seed + 2)
        for n in bl:
            n.start += s_finish
            n.end += s_finish
            n.velocity = min(127, n.velocity + 20)
            if n.start < c.duration:
                drums_inst.notes.append(n)

        de_bass = driving_eighths(root=dm_root, bars=max(1, finish_bars), tempo=145,
                                   time_sig=(4, 4), velocity=127)
        for n in de_bass:
            n.start += s_finish
            n.end += s_finish
            if n.start < c.duration:
                bass_inst.notes.append(n)

        pitches = chord("D", "min", octave=2, voicing="closed")
        for p in pitches:
            chords_inst.notes.append(pretty_midi.Note(velocity=127, pitch=p,
                                      start=s_finish, end=min(c.duration, s_finish + bar)))

        # Cluster at finish
        cluster_pitches = cluster(center_pitch=62, width=2)
        for cp in cluster_pitches:
            chords_inst.notes.append(pretty_midi.Note(velocity=120, pitch=cp,
                                      start=s_finish, end=s_finish + beat * 0.3))

        mel_finish = contour("Dm", "phrygian", direction="ascending", num_notes=12,
                             octave=4, seed=c.seed + 3, start_time=s_finish,
                             note_duration=beat * 0.4, note_gap=beat * 0.08, velocity=120)
        for n in mel_finish:
            if n.start < c.duration:
                melody_inst.notes.append(n)

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
