import pretty_midi
from lib.directives import (
    collapse_plan, loop_that_breaks, two_songs_stitched_plan,
    countdown_plan, unison_collapse, reverse_structure_plan,
    rhythmic_displacement, drone,
)


class TestCollapsePlan:
    def test_returns_bar_boundaries(self):
        plan = collapse_plan(total_bars=16, collapse_bar=8, re_entry_bar=12)
        assert plan["before"] == (0, 8)
        assert plan["solo"] == (8, 12)
        assert plan["after"] == (12, 16)


class TestLoopThatBreaks:
    def test_mutations_accumulate(self):
        base_notes = [
            pretty_midi.Note(velocity=100, pitch=60, start=0.0, end=0.5),
            pretty_midi.Note(velocity=100, pitch=64, start=0.5, end=1.0),
            pretty_midi.Note(velocity=100, pitch=67, start=1.0, end=1.5),
        ]
        result = loop_that_breaks(base_notes, repetitions=4, seed=42)
        assert len(result) == 4
        assert len(result[0]) == 3
        assert all(r.pitch == o.pitch for r, o in zip(result[0], base_notes))
        last = result[-1]
        pitches_orig = [n.pitch for n in base_notes]
        pitches_last = [n.pitch for n in last]
        assert pitches_orig != pitches_last or len(last) != len(base_notes)


class TestTwoSongsStitchedPlan:
    def test_returns_three_sections(self):
        plan = two_songs_stitched_plan(total_bars=16, split_bar=7, transition_bars=2)
        assert plan["song_a"] == (0, 7)
        assert plan["transition"] == (7, 9)
        assert plan["song_b"] == (9, 16)


class TestCountdownPlan:
    def test_default_sections(self):
        plan = countdown_plan(tempo=120, time_sig=(4, 4))
        assert plan["section_bars"] == [8, 4, 2, 1]
        assert len(plan["bar_boundaries"]) == 4
        assert plan["bar_boundaries"][0] == (0, 8)
        assert plan["bar_boundaries"][1] == (8, 12)
        assert plan["bar_boundaries"][2] == (12, 14)
        assert plan["bar_boundaries"][3] == (14, 15)

    def test_custom_sections(self):
        plan = countdown_plan(tempo=120, time_sig=(4, 4), section_bars=[4, 2, 1])
        assert plan["section_bars"] == [4, 2, 1]


class TestUnisonCollapse:
    def test_returns_notes_on_target_pitch(self):
        notes = unison_collapse(
            target_pitch=60,
            num_instruments=4,
            start=5.0,
            duration=2.0,
            velocity=80,
        )
        assert len(notes) == 4
        for n in notes:
            assert n.pitch == 60 or n.pitch == 60 + 12 or n.pitch == 60 - 12
            assert n.start == 5.0
            assert n.end == 7.0


class TestReverseStructurePlan:
    def test_instruments_decrease(self):
        plan = reverse_structure_plan(total_bars=16, num_instruments=4)
        assert len(plan) >= 2
        assert plan[0]["num_instruments"] == 4
        assert plan[-1]["num_instruments"] == 1


class TestRhythmicDisplacement:
    def test_shifts_by_eighth(self):
        notes = [
            pretty_midi.Note(velocity=100, pitch=60, start=0.0, end=0.5),
            pretty_midi.Note(velocity=100, pitch=64, start=0.5, end=1.0),
        ]
        result = rhythmic_displacement(notes, offset_eighths=1, tempo=120)
        eighth = 60.0 / 120 / 2.0
        assert abs(result[0].start - eighth) < 0.001
        assert abs(result[1].start - (0.5 + eighth)) < 0.001


class TestDrone:
    def test_returns_single_sustained_note(self):
        note = drone(pitch=28, duration=30.0, velocity=45)
        assert isinstance(note, pretty_midi.Note)
        assert note.pitch == 28
        assert note.start == 0.0
        assert note.end == 30.0
        assert note.velocity == 45
