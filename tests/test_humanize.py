import pretty_midi
from lib.humanize import humanize_timing, humanize_velocity, strum, ghost_notes, SeededRng


def _make_notes(count, start=0.0, step=0.5, pitch=60, vel=100, dur=0.25):
    """Helper: create evenly spaced notes."""
    return [
        pretty_midi.Note(velocity=vel, pitch=pitch, start=start + i * step, end=start + i * step + dur)
        for i in range(count)
    ]


class TestSeededRng:
    def test_deterministic(self):
        rng1 = SeededRng(42)
        rng2 = SeededRng(42)
        vals1 = [rng1.uniform(-1, 1) for _ in range(10)]
        vals2 = [rng2.uniform(-1, 1) for _ in range(10)]
        assert vals1 == vals2

    def test_different_seeds_differ(self):
        rng1 = SeededRng(1)
        rng2 = SeededRng(2)
        vals1 = [rng1.uniform(-1, 1) for _ in range(10)]
        vals2 = [rng2.uniform(-1, 1) for _ in range(10)]
        assert vals1 != vals2

    def test_randint(self):
        rng = SeededRng(99)
        for _ in range(50):
            val = rng.randint(0, 10)
            assert 0 <= val <= 10


class TestHumanizeTiming:
    def test_offsets_notes(self):
        notes = _make_notes(4, start=1.0)
        result = humanize_timing(notes, spread_ms=10, seed=42)
        assert len(result) == 4
        for orig, hum in zip(notes, result):
            assert abs(hum.start - orig.start) <= 0.010
            assert hum.pitch == orig.pitch
            assert hum.velocity == orig.velocity

    def test_no_negative_start(self):
        notes = _make_notes(1, start=0.001)
        result = humanize_timing(notes, spread_ms=50, seed=42)
        assert result[0].start >= 0.0

    def test_deterministic(self):
        notes = _make_notes(4)
        r1 = humanize_timing(notes, spread_ms=10, seed=42)
        r2 = humanize_timing(notes, spread_ms=10, seed=42)
        assert [n.start for n in r1] == [n.start for n in r2]


class TestHumanizeVelocity:
    def test_varies_velocity(self):
        notes = _make_notes(10, vel=80)
        result = humanize_velocity(notes, spread=15, seed=42)
        velocities = [n.velocity for n in result]
        assert len(set(velocities)) > 1
        assert all(1 <= v <= 127 for v in velocities)

    def test_deterministic(self):
        notes = _make_notes(10, vel=80)
        r1 = humanize_velocity(notes, spread=15, seed=42)
        r2 = humanize_velocity(notes, spread=15, seed=42)
        assert [n.velocity for n in r1] == [n.velocity for n in r2]


class TestStrum:
    def test_down_strum_lowest_first(self):
        notes = [
            pretty_midi.Note(velocity=100, pitch=40, start=1.0, end=2.0),
            pretty_midi.Note(velocity=100, pitch=52, start=1.0, end=2.0),
            pretty_midi.Note(velocity=100, pitch=64, start=1.0, end=2.0),
        ]
        result = strum(notes, direction="down", spread_ms=20)
        starts = [n.start for n in result]
        assert starts[0] < starts[1] < starts[2]
        assert starts[-1] - starts[0] <= 0.020 + 1e-9  # float tolerance

    def test_up_strum_highest_first(self):
        notes = [
            pretty_midi.Note(velocity=100, pitch=40, start=1.0, end=2.0),
            pretty_midi.Note(velocity=100, pitch=52, start=1.0, end=2.0),
            pretty_midi.Note(velocity=100, pitch=64, start=1.0, end=2.0),
        ]
        result = strum(notes, direction="up", spread_ms=20)
        starts = [n.start for n in result]
        assert starts[2] < starts[1] < starts[0]


class TestGhostNotes:
    def test_inserts_ghost_notes(self):
        notes = _make_notes(4, step=0.5, vel=100)
        result = ghost_notes(notes, probability=1.0, vel_range=(15, 40), seed=42)
        assert len(result) > len(notes)
        originals = set((n.start, n.pitch) for n in notes)
        for n in result:
            if (n.start, n.pitch) not in originals:
                assert 15 <= n.velocity <= 40

    def test_probability_zero_no_ghosts(self):
        notes = _make_notes(4, step=0.5, vel=100)
        result = ghost_notes(notes, probability=0.0, vel_range=(15, 40), seed=42)
        assert len(result) == len(notes)
