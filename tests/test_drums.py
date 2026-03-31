import pretty_midi
from lib.drums import driving_emo, blast, half_time, floor_tom_pulse, no_snare, fill
from lib.constants import KICK, SNARE, HAT_CLOSED, HAT_OPEN, FLOOR_TOM, RACK_TOM


class TestDrivingEmo:
    def test_returns_notes(self):
        notes = driving_emo(bars=2, tempo=120, time_sig=(4, 4), seed=42)
        assert len(notes) > 0
        for n in notes:
            assert isinstance(n, pretty_midi.Note)

    def test_contains_kick_snare_hat(self):
        notes = driving_emo(bars=2, tempo=120, time_sig=(4, 4), seed=42)
        pitches = {n.pitch for n in notes}
        assert KICK in pitches
        assert SNARE in pitches
        assert HAT_CLOSED in pitches or HAT_OPEN in pitches

    def test_kick_on_1_and_3(self):
        notes = driving_emo(bars=1, tempo=120, time_sig=(4, 4), seed=42)
        kick_notes = [n for n in notes if n.pitch == KICK]
        kick_starts = sorted(n.start for n in kick_notes)
        beat_dur = 60.0 / 120
        assert any(abs(t - 0.0) < 0.02 for t in kick_starts)
        assert any(abs(t - beat_dur * 2) < 0.02 for t in kick_starts)


class TestBlast:
    def test_alternating_kick_snare(self):
        notes = blast(bars=1, tempo=120, time_sig=(4, 4), seed=42)
        kick_snare = [n for n in notes if n.pitch in (KICK, SNARE)]
        assert len(kick_snare) >= 14

    def test_capped_at_4_bars(self):
        notes_4 = blast(bars=4, tempo=120, time_sig=(4, 4), seed=42)
        notes_8 = blast(bars=8, tempo=120, time_sig=(4, 4), seed=42)
        max_time_4 = max(n.end for n in notes_4)
        max_time_8 = max(n.end for n in notes_8)
        assert abs(max_time_4 - max_time_8) < 0.1


class TestHalfTime:
    def test_snare_on_beat_3(self):
        notes = half_time(bars=2, tempo=120, time_sig=(4, 4), seed=42)
        snare_notes = [n for n in notes if n.pitch == SNARE]
        beat_dur = 60.0 / 120
        for sn in snare_notes:
            bar_pos = sn.start % (beat_dur * 4)
            assert abs(bar_pos - beat_dur * 2) < 0.02


class TestFloorTomPulse:
    def test_no_kick(self):
        notes = floor_tom_pulse(bars=2, tempo=120, time_sig=(4, 4), seed=42)
        pitches = {n.pitch for n in notes}
        assert KICK not in pitches
        assert FLOOR_TOM in pitches


class TestNoSnare:
    def test_no_snare_pitch(self):
        notes = no_snare(bars=2, tempo=120, time_sig=(4, 4), seed=42)
        pitches = {n.pitch for n in notes}
        assert SNARE not in pitches
        assert KICK in pitches or FLOOR_TOM in pitches
        assert HAT_CLOSED in pitches or HAT_OPEN in pitches


class TestFill:
    def test_short_fill(self):
        notes = fill(beats=1, tempo=120, seed=42)
        assert len(notes) > 0
        max_time = max(n.end for n in notes)
        beat_dur = 60.0 / 120
        assert max_time <= beat_dur * 1.5

    def test_uses_toms_or_snare(self):
        notes = fill(beats=2, tempo=120, seed=42)
        pitches = {n.pitch for n in notes}
        fill_instruments = {SNARE, FLOOR_TOM, RACK_TOM}
        assert len(pitches & fill_instruments) > 0
