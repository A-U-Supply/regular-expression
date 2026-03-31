from lib.harmony import chord, progression, cluster, chromatic_mediant, pedal_point
from lib.constants import SCALES, KEY_PALETTE
import pretty_midi


class TestChord:
    def test_minor_chord_closed(self):
        pitches = chord("A", "min", octave=3, voicing="closed")
        assert 57 in pitches  # root
        assert 60 in pitches  # minor 3rd
        assert 64 in pitches  # perfect 5th

    def test_minor_chord_open_pitch_classes(self):
        pitches = chord("A", "min", octave=3)
        pcs = {p % 12 for p in pitches}
        assert 9 in pcs   # A
        assert 0 in pcs   # C (minor 3rd)
        assert 4 in pcs   # E (perfect 5th)

    def test_power_chord(self):
        pitches = chord("E", "power", octave=2)
        assert 40 in pitches
        assert 47 in pitches
        assert len(pitches) == 2

    def test_open_voicing_spans_octaves(self):
        pitches = chord("A", "min", octave=2, voicing="open")
        assert max(pitches) - min(pitches) >= 12

    def test_closed_voicing_compact(self):
        pitches = chord("A", "min", octave=3, voicing="closed")
        assert max(pitches) - min(pitches) <= 12

    def test_sus2(self):
        pitches = chord("A", "sus2", octave=3, voicing="closed")
        assert 57 in pitches
        assert 59 in pitches
        assert 64 in pitches

    def test_sus4(self):
        pitches = chord("A", "sus4", octave=3, voicing="closed")
        assert 57 in pitches
        assert 62 in pitches
        assert 64 in pitches

    def test_dim(self):
        pitches = chord("A", "dim", octave=3, voicing="closed")
        assert 57 in pitches
        assert 60 in pitches
        assert 63 in pitches

    def test_aug(self):
        pitches = chord("A", "aug", octave=3, voicing="closed")
        assert 57 in pitches
        assert 61 in pitches
        assert 65 in pitches


class TestProgression:
    def test_returns_list_of_chord_pitch_lists(self):
        result = progression("Am", ["i", "III", "VII", "iv"], bars=4, time_sig=(4, 4))
        assert len(result) == 4
        for chord_pitches in result:
            assert isinstance(chord_pitches, list)
            assert all(isinstance(p, int) for p in chord_pitches)

    def test_i_chord_contains_root(self):
        result = progression("Am", ["i"], bars=1, time_sig=(4, 4))
        assert any(p % 12 == 9 for p in result[0])


class TestCluster:
    def test_cluster_width(self):
        pitches = cluster(60, width=2)
        assert len(pitches) == 5
        assert min(pitches) == 58
        assert max(pitches) == 62

    def test_cluster_width_1(self):
        pitches = cluster(60, width=1)
        assert len(pitches) == 3
        assert pitches == [59, 60, 61]


class TestChromaticMediant:
    def test_major_third_up(self):
        new_root = chromatic_mediant(57, "major_up")
        assert new_root == 61

    def test_minor_third_down(self):
        new_root = chromatic_mediant(57, "minor_down")
        assert new_root == 54


class TestPedalPoint:
    def test_returns_note(self):
        note = pedal_point(40, duration=30.0, velocity=50)
        assert isinstance(note, pretty_midi.Note)
        assert note.pitch == 40
        assert note.start == 0.0
        assert note.end == 30.0
        assert note.velocity == 50
