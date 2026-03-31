"""Smoke test: create a minimal track using all lib modules and verify MIDI output."""

import os
import pretty_midi
from lib.composer import Composer
from lib.constants import BASS_FINGER, GUITAR_OVERDRIVE, GUITAR_DISTORTION, DRUM_CHANNEL
from lib.drums import driving_emo
from lib.harmony import progression, pedal_point
from lib.melody import phrase, spike
from lib.bass import driving_eighths
from lib.humanize import humanize_timing, humanize_velocity, strum
from lib.directives import drone


class TestFullPipeline:
    def test_generate_minimal_track(self, tmp_path):
        c = Composer(99, "test_track", key="Am", tempo=120, time_sig=(4, 4), seed=1)

        # Drums
        drums = c.add_instrument("Drums", program=0, channel=9)
        drum_notes = driving_emo(bars=4, tempo=120, time_sig=(4, 4), seed=1)
        drums.notes.extend(drum_notes)

        # Bass
        bass = c.add_instrument("Bass", program=BASS_FINGER)
        bass_notes = driving_eighths(root=40, bars=4, tempo=120)
        bass_notes = humanize_timing(bass_notes, spread_ms=5, seed=1)
        bass_notes = humanize_velocity(bass_notes, spread=10, seed=1)
        bass.notes.extend(bass_notes)

        # Chords
        chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
        chord_pitches = progression("Am", ["i", "III", "VII", "iv"], bars=4, time_sig=(4, 4))
        for i, pitches in enumerate(chord_pitches):
            bar_start = i * c.bar_duration
            for p in pitches:
                chords_inst.notes.append(pretty_midi.Note(
                    velocity=90, pitch=p, start=bar_start, end=bar_start + c.bar_duration * 0.9,
                ))

        # Melody
        melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)
        mel_notes = phrase("Am", "natural_minor", bars=4, tempo=120, time_sig=(4, 4), seed=1)
        melody_inst.notes.extend(mel_notes)

        # Write MIDI
        out_dir = str(tmp_path)
        path = c.write_midi(output_dir=out_dir)
        assert os.path.exists(path)

        # Verify structure
        loaded = pretty_midi.PrettyMIDI(path)
        assert len(loaded.instruments) == 4
        for inst in loaded.instruments:
            assert len(inst.notes) > 0

    def test_seed_determinism(self, tmp_path):
        """Same seed produces identical MIDI output."""
        def make_track(seed, out_dir):
            c = Composer(99, "det_test", key="Em", tempo=140, time_sig=(4, 4), seed=seed)
            drums = c.add_instrument("Drums", program=0, channel=9)
            drums.notes.extend(driving_emo(bars=2, tempo=140, seed=seed))
            bass = c.add_instrument("Bass", program=BASS_FINGER)
            bass.notes.extend(driving_eighths(root=40, bars=2, tempo=140))
            return c.write_midi(output_dir=out_dir)

        dir1 = str(tmp_path / "run1")
        dir2 = str(tmp_path / "run2")
        path1 = make_track(42, dir1)
        path2 = make_track(42, dir2)

        midi1 = pretty_midi.PrettyMIDI(path1)
        midi2 = pretty_midi.PrettyMIDI(path2)
        for i1, i2 in zip(midi1.instruments, midi2.instruments):
            assert len(i1.notes) == len(i2.notes)
            for n1, n2 in zip(i1.notes, i2.notes):
                assert n1.pitch == n2.pitch
                assert abs(n1.start - n2.start) < 0.0001
                assert n1.velocity == n2.velocity
