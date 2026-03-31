#!/usr/bin/env python
"""Track 25: fucking useless — Slow waltz, Am Dorian, 92bpm. All instruments
collapse to A unison. Unison Collapse directive."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pretty_midi
from lib.composer import Composer
from lib.constants import (BASS_FINGER, GUITAR_DISTORTION, PAD_WARM,
                           DRUM_CHANNEL, CRASH, KICK, FLOOR_TOM)
from lib.drums import half_time, floor_tom_pulse, driving_emo
from lib.harmony import chord
from lib.melody import contour, phrase, broken_trail
from lib.bass import locked_bass
from lib.humanize import strum, SeededRng
from lib.directives import unison_collapse
from lib.cli import parse_track_args


def generate(seed=None):
    c = Composer(25, "fucking_useless", key="Am", tempo=92, time_sig=(3, 4), seed=seed)
    rng = SeededRng(c.seed)
    beat = c.beat_duration
    bar = c.bar_duration  # 3 beats

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_FINGER)
    chords_inst = c.add_instrument("Chords", program=PAD_WARM)
    melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)

    # Am Dorian: A B C D E F# G
    chord_seq = [("A", "min"), ("D", "min"), ("E", "min"), ("A", "min")]
    am_root = 33  # A1

    # Bars: ~14 at this tempo
    total_bars = c.bars
    collapse_bar = total_bars - 4  # Collapse 4 bars from end
    re_entry_bar = total_bars - 2  # 2 bar re-entry

    # === Section 1: Before collapse — slow waltz ===
    pre_bars = collapse_bar

    ht = half_time(bars=pre_bars, tempo=92, time_sig=(3, 4), seed=c.seed)
    drums_inst.notes.extend(ht)

    kick_times = [i * bar + b * beat for i in range(pre_bars) for b in [0, 1]]
    bass_pre = locked_bass(kick_times, root=am_root, fifth=40, bars=pre_bars,
                           tempo=92, seed=c.seed, velocity=80)
    bass_inst.notes.extend(bass_pre)

    for i in range(pre_bars):
        t = i * bar
        root, q = chord_seq[i % 4]
        pitches = chord(root, q, octave=2, voicing="open")
        cn = [pretty_midi.Note(velocity=65 + rng.randint(-5, 5), pitch=p,
                               start=t, end=t + bar * 0.85) for p in pitches]
        chords_inst.notes.extend(strum(cn, direction="down", spread_ms=40))

    mel_pre = contour("Am", "dorian", direction="descending", num_notes=pre_bars * 2,
                      octave=4, seed=c.seed, start_time=0.0,
                      note_duration=beat * 0.8, note_gap=beat * 0.4, velocity=75)
    melody_inst.notes.extend(mel_pre)

    # === Collapse: all instruments converge on A ===
    s_collapse = collapse_bar * bar
    collapse_dur = (re_entry_bar - collapse_bar) * bar

    # Unison notes
    uni_notes = unison_collapse(target_pitch=57, num_instruments=4,
                                start=s_collapse, duration=collapse_dur, velocity=100)
    # Assign to instruments: A1=33, A2=45, A3=57, A4=69
    bass_inst.notes.append(pretty_midi.Note(velocity=100, pitch=33,
                           start=s_collapse, end=s_collapse + collapse_dur))
    chords_inst.notes.append(pretty_midi.Note(velocity=100, pitch=45,
                              start=s_collapse, end=s_collapse + collapse_dur))
    melody_inst.notes.append(pretty_midi.Note(velocity=100, pitch=57,
                              start=s_collapse, end=s_collapse + collapse_dur))

    # Floor tom pulse during collapse
    ft = floor_tom_pulse(bars=re_entry_bar - collapse_bar, tempo=92, time_sig=(3, 4), seed=c.seed + 1)
    for n in ft:
        n.start += s_collapse
        n.end += s_collapse
        if n.start < c.duration:
            drums_inst.notes.append(n)

    # === Re-entry: final 2 bars — crash back, fortissimo ===
    s_re = re_entry_bar * bar
    if s_re < c.duration:
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=CRASH,
                                start=s_re, end=s_re + 0.4))
        drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=KICK,
                                start=s_re, end=s_re + 0.1))

        de_re = driving_emo(bars=2, tempo=92, time_sig=(3, 4), seed=c.seed + 2)
        for n in de_re:
            n.start += s_re
            n.end += s_re
            n.velocity = min(127, n.velocity + 20)
            if n.start < c.duration:
                drums_inst.notes.append(n)

        pitches = chord("A", "min", octave=2, voicing="open")
        for p in pitches:
            chords_inst.notes.append(pretty_midi.Note(velocity=120, pitch=p,
                                      start=s_re, end=min(c.duration, s_re + bar)))
        bass_inst.notes.append(pretty_midi.Note(velocity=120, pitch=am_root,
                               start=s_re, end=min(c.duration, s_re + bar)))
        melody_inst.notes.append(pretty_midi.Note(velocity=120, pitch=69,  # A4
                                  start=s_re, end=min(c.duration, s_re + beat * 2)))

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
