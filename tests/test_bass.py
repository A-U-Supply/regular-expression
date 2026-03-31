import pretty_midi
from lib.bass import locked_bass, driving_eighths, counter_melody, chromatic_approach


class TestLockedBass:
    def test_returns_notes(self):
        kick_times = [0.0, 1.0, 2.0, 3.0]
        notes = locked_bass(kick_times, root=40, fifth=47, bars=4, tempo=120, seed=42)
        assert len(notes) > 0
        for n in notes:
            assert isinstance(n, pretty_midi.Note)
            assert n.pitch in (40, 47, 52)

    def test_some_notes_align_with_kicks(self):
        kick_times = [0.0, 0.5, 1.0, 1.5]
        notes = locked_bass(kick_times, root=40, fifth=47, bars=2, tempo=120, seed=42)
        note_starts = {round(n.start, 2) for n in notes}
        kick_set = {round(t, 2) for t in kick_times}
        assert len(note_starts & kick_set) > 0


class TestDrivingEighths:
    def test_note_count(self):
        notes = driving_eighths(root=40, bars=2, tempo=120, time_sig=(4, 4))
        assert len(notes) == 16

    def test_all_same_pitch(self):
        notes = driving_eighths(root=40, bars=1, tempo=120, time_sig=(4, 4))
        assert all(n.pitch == 40 for n in notes)


class TestCounterMelody:
    def test_returns_notes(self):
        notes = counter_melody("Am", "natural_minor", bars=4, tempo=120, time_sig=(4, 4), seed=42)
        assert len(notes) > 0
        for n in notes:
            assert isinstance(n, pretty_midi.Note)

    def test_uses_wide_intervals(self):
        notes = counter_melody("Am", "natural_minor", bars=4, tempo=120, time_sig=(4, 4), seed=42)
        if len(notes) >= 2:
            intervals = [abs(notes[i + 1].pitch - notes[i].pitch) for i in range(len(notes) - 1)]
            assert any(iv >= 7 for iv in intervals)


class TestChromaticApproach:
    def test_ascending(self):
        notes = chromatic_approach(target=40, direction="up", length=4, start=0.0, note_duration=0.2)
        assert len(notes) == 4
        assert notes[-1].pitch == 40
        for i in range(len(notes) - 1):
            assert notes[i + 1].pitch == notes[i].pitch + 1

    def test_descending(self):
        notes = chromatic_approach(target=40, direction="down", length=3, start=0.0, note_duration=0.2)
        assert len(notes) == 3
        assert notes[-1].pitch == 40
        for i in range(len(notes) - 1):
            assert notes[i + 1].pitch == notes[i].pitch - 1
