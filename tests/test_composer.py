import os
import pretty_midi
from lib.composer import Composer


class TestComposer:
    def test_creates_midi_object(self):
        c = Composer(1, "wtf", key="Am", tempo=130, time_sig=(4, 4))
        assert c.track_number == 1
        assert c.title == "wtf"
        assert c.tempo == 130
        assert c.duration == 30.0

    def test_add_instrument(self):
        c = Composer(1, "wtf", key="Am", tempo=130, time_sig=(4, 4))
        inst = c.add_instrument("Bass", program=33)
        assert isinstance(inst, pretty_midi.Instrument)
        assert inst.program == 33

    def test_add_drum_instrument(self):
        c = Composer(1, "wtf", key="Am", tempo=130, time_sig=(4, 4))
        inst = c.add_instrument("Drums", program=0, channel=9)
        assert inst.is_drum is True

    def test_write_midi(self, tmp_path):
        c = Composer(1, "wtf", key="Am", tempo=130, time_sig=(4, 4))
        bass = c.add_instrument("Bass", program=33)
        bass.notes.append(pretty_midi.Note(velocity=100, pitch=40, start=0.0, end=1.0))
        out_path = str(tmp_path / "01_wtf.mid")
        c.write_midi(output_dir=str(tmp_path))
        assert os.path.exists(out_path)
        loaded = pretty_midi.PrettyMIDI(out_path)
        assert len(loaded.instruments) == 1

    def test_filename_format(self):
        c = Composer(3, "ffs", key="Em", tempo=140, time_sig=(4, 4))
        assert c.filename == "03_ffs.mid"

    def test_filename_spaces_to_underscores(self):
        c = Composer(14, "piece of shit", key="Bm", tempo=100, time_sig=(4, 4))
        assert c.filename == "14_piece_of_shit.mid"

    def test_seed_default(self):
        c = Composer(5, "shit", key="Am", tempo=120, time_sig=(4, 4))
        assert c.seed == 5

    def test_seed_override(self):
        c = Composer(5, "shit", key="Am", tempo=120, time_sig=(4, 4), seed=42)
        assert c.seed == 42

    def test_bars_property(self):
        c = Composer(1, "wtf", key="Am", tempo=120, time_sig=(4, 4))
        assert c.bars == 15

    def test_bars_property_odd_meter(self):
        c = Composer(1, "wtf", key="Am", tempo=120, time_sig=(7, 8))
        assert c.bars == 17

    def test_beat_duration(self):
        c = Composer(1, "wtf", key="Am", tempo=120, time_sig=(4, 4))
        assert abs(c.beat_duration - 0.5) < 0.001

    def test_bar_duration(self):
        c = Composer(1, "wtf", key="Am", tempo=120, time_sig=(4, 4))
        assert abs(c.bar_duration - 2.0) < 0.001
