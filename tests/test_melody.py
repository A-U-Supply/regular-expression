import pretty_midi
from lib.melody import scale_pitches, contour, phrase, spike, stutter, broken_trail


class TestScalePitches:
    def test_a_natural_minor(self):
        pitches = scale_pitches("Am", "natural_minor", octave=4, num_octaves=1)
        assert pitches == [69, 71, 72, 74, 76, 77, 79]

    def test_e_phrygian(self):
        pitches = scale_pitches("Em", "phrygian", octave=3, num_octaves=1)
        assert pitches == [52, 53, 55, 57, 59, 60, 62]


class TestContour:
    def test_descending_stays_in_range(self):
        notes = contour("Am", "natural_minor", direction="descending", num_notes=8, octave=4, seed=42)
        assert len(notes) == 8
        for n in notes:
            assert isinstance(n, pretty_midi.Note)
        assert notes[0].pitch >= notes[-1].pitch

    def test_ascending(self):
        notes = contour("Am", "natural_minor", direction="ascending", num_notes=8, octave=4, seed=42)
        assert notes[0].pitch <= notes[-1].pitch


class TestPhrase:
    def test_returns_notes_with_gaps(self):
        notes = phrase("Am", "natural_minor", bars=4, tempo=120, time_sig=(4, 4), density=0.6, seed=42)
        assert len(notes) > 0
        for n in notes:
            assert n.start >= 0.0
            assert n.end <= 30.5

    def test_density_affects_count(self):
        sparse = phrase("Am", "natural_minor", bars=4, tempo=120, time_sig=(4, 4), density=0.3, seed=42)
        dense = phrase("Am", "natural_minor", bars=4, tempo=120, time_sig=(4, 4), density=0.9, seed=42)
        assert len(dense) > len(sparse)


class TestSpike:
    def test_spike_returns_two_notes(self):
        notes = spike(base_pitch=60, interval="min7", start=1.0, velocity=100)
        assert len(notes) == 2
        assert notes[0].pitch == 70
        assert notes[1].pitch == 60

    def test_octave_spike(self):
        notes = spike(base_pitch=60, interval="octave", start=1.0, velocity=100)
        assert notes[0].pitch == 72


class TestStutter:
    def test_repeated_notes(self):
        notes = stutter(pitch=64, count=6, note_duration=0.1, gap=0.05, start=0.0, velocity=90)
        assert len(notes) == 6
        assert all(n.pitch == 64 for n in notes)
        assert all(n.velocity == 90 for n in notes)
        for i in range(1, len(notes)):
            assert notes[i].start > notes[i - 1].start


class TestBrokenTrail:
    def test_truncates_and_fades(self):
        original = [
            pretty_midi.Note(velocity=100, pitch=60, start=0.0, end=0.5),
            pretty_midi.Note(velocity=100, pitch=62, start=0.5, end=1.0),
            pretty_midi.Note(velocity=100, pitch=64, start=1.0, end=1.5),
            pretty_midi.Note(velocity=100, pitch=65, start=1.5, end=2.0),
        ]
        result = broken_trail(original, decay_point=2)
        assert result[0].velocity == 100
        assert result[1].velocity == 100
        assert result[2].velocity < 100
        assert result[3].velocity < result[2].velocity
