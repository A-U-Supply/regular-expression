#!/usr/bin/env python
"""Track 04: omfg — Peak unhinged. Two completely different songs crammed into
30 seconds. Dm waltz → noise transition → F#m assault. Tritone key shift."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


import pretty_midi
from lib.composer import Composer
from lib.constants import BASS_FINGER, GUITAR_OVERDRIVE, GUITAR_DISTORTION, PAD_WARM, DRUM_CHANNEL
from lib.drums import driving_emo, half_time, fill
from lib.harmony import chord, cluster
from lib.melody import contour, stutter
from lib.bass import locked_bass, driving_eighths
from lib.humanize import humanize_timing, humanize_velocity, strum, SeededRng
from lib.directives import two_songs_stitched_plan
from lib.cli import parse_track_args
from lib.constants import CRASH, KICK, SNARE, FLOOR_TOM


def generate(seed=None):
    # Use base tempo for the Composer, but sections have different tempos
    c = Composer(4, "omfg", key="Dm", tempo=110, time_sig=(3, 4), seed=seed)
    rng = SeededRng(c.seed)

    drums_inst = c.add_instrument("Drums", program=0, channel=9)
    bass_inst = c.add_instrument("Bass", program=BASS_FINGER)
    chords_inst = c.add_instrument("Chords", program=PAD_WARM)
    melody_inst = c.add_instrument("Melody", program=GUITAR_OVERDRIVE)

    # Plan: Song A ~10s, transition ~2s, Song B ~18s
    song_a_end = 10.0
    transition_end = 12.0

    # =============================================
    # SONG A: D minor, 110 BPM, 3/4 (woozy waltz)
    # =============================================
    tempo_a = 110.0
    beat_a = 60.0 / tempo_a
    bar_a = 3 * beat_a  # 3/4 time
    bars_a = int(song_a_end / bar_a)

    # Dorian progression: i-VI-III-VII = Dm-Bb-F-C
    chord_seq_a = [("D", "min"), ("A#", "min"), ("F", "min"), ("C", "min")]

    # Drums: half-time waltz feel
    ht_notes = half_time(bars=bars_a, tempo=tempo_a, time_sig=(3, 4), seed=c.seed)
    drums_inst.notes.extend(ht_notes)

    # Chords: wide open pad voicings
    for bar_idx in range(bars_a):
        t = bar_idx * bar_a
        root, quality = chord_seq_a[bar_idx % 4]
        pitches = chord(root, quality, octave=2, voicing="open")
        chord_notes = [pretty_midi.Note(velocity=65 + rng.randint(-5, 5), pitch=p,
                       start=t, end=t + bar_a * 0.9) for p in pitches]
        chords_inst.notes.extend(strum(chord_notes, direction="down", spread_ms=30))

    # Melody: descending, gentle
    mel_a = contour("Dm", "dorian", direction="descending", num_notes=12,
                    octave=4, seed=c.seed, start_time=beat_a,
                    note_duration=beat_a * 1.5, note_gap=beat_a * 0.5, velocity=70)
    melody_inst.notes.extend(mel_a)

    # Bass: simple roots
    for bar_idx in range(bars_a):
        t = bar_idx * bar_a
        root_pitches = [38, 34, 29, 36]  # D2, Bb1, F1, C2
        bass_inst.notes.append(pretty_midi.Note(velocity=75, pitch=root_pitches[bar_idx % 4],
                               start=t, end=t + bar_a * 0.8))

    # =============================================
    # TRANSITION: ~2 seconds of chaos
    # =============================================
    trans_start = song_a_end

    # Cluster chord
    cluster_pitches = cluster(54, width=3)  # F#3 area — bridging the two keys
    for cp in cluster_pitches:
        chords_inst.notes.append(pretty_midi.Note(velocity=rng.randint(70, 110), pitch=cp,
                                 start=trans_start, end=transition_end))

    # Arrhythmic drum hits
    for i in range(8):
        t = trans_start + rng.uniform(0.0, 2.0)
        pitch = [KICK, SNARE, FLOOR_TOM][rng.randint(0, 2)]
        drums_inst.notes.append(pretty_midi.Note(velocity=rng.randint(60, 127), pitch=pitch,
                                start=t, end=t + 0.1))

    # Random velocity bass stabs
    for i in range(6):
        t = trans_start + rng.uniform(0.0, 2.0)
        bass_inst.notes.append(pretty_midi.Note(velocity=rng.randint(40, 120),
                               pitch=rng.randint(28, 42), start=t, end=t + 0.15))

    # =============================================
    # SONG B: F# minor, 148 BPM, 4/4 (violent)
    # =============================================
    tempo_b = 148.0
    beat_b = 60.0 / tempo_b
    bar_b = 4 * beat_b
    song_b_start = transition_end
    remaining_time = c.duration - song_b_start
    bars_b = int(remaining_time / bar_b)

    # Switch chords instrument to distortion for Song B
    chords_b_inst = c.add_instrument("Chords B", program=GUITAR_DISTORTION)

    # Phrygian progression: i-iv-bII-i = F#m-Bm-Gm-F#m
    chord_seq_b = [("F#", "min"), ("B", "min"), ("G", "min"), ("F#", "min")]

    # Crash at the start of Song B
    drums_inst.notes.append(pretty_midi.Note(velocity=127, pitch=CRASH,
                            start=song_b_start, end=song_b_start + 0.4))

    # Drums: driving emo, aggressive
    drum_b = driving_emo(bars=bars_b, tempo=tempo_b, time_sig=(4, 4), seed=c.seed + 10)
    for n in drum_b:
        n.start += song_b_start
        n.end += song_b_start
        n.velocity = min(127, n.velocity + 10)
    drums_inst.notes.extend(drum_b)

    # Power chords
    for bar_idx in range(bars_b):
        t = song_b_start + bar_idx * bar_b
        if t >= c.duration:
            break
        root, _ = chord_seq_b[bar_idx % 4]
        pitches = chord(root, "power", octave=2)
        for p in pitches:
            chords_b_inst.notes.append(pretty_midi.Note(velocity=115, pitch=p,
                                       start=t, end=min(t + bar_b * 0.9, c.duration)))

    # Rising melody — opposite of Song A's descent
    mel_b = contour("F#m", "phrygian", direction="ascending", num_notes=16,
                    octave=4, seed=c.seed + 11, start_time=song_b_start,
                    note_duration=beat_b * 0.7, note_gap=beat_b * 0.3, velocity=105)
    for n in mel_b:
        if n.start < c.duration:
            melody_inst.notes.append(n)

    # Bass: driving eighths on F#
    bass_b = driving_eighths(root=30, bars=bars_b, tempo=tempo_b, velocity=110)  # F#1
    for n in bass_b:
        n.start += song_b_start
        n.end += song_b_start
        if n.start < c.duration:
            bass_inst.notes.append(n)

    c.write_midi()
    return c


if __name__ == "__main__":
    args = parse_track_args()
    c = generate(seed=args.seed)
    if not args.no_render:
        c.render()
