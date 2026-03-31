import os
import subprocess
import pytest
import pretty_midi
from lib.render import render_wav


@pytest.fixture
def midi_file(tmp_path):
    """Create a minimal MIDI file for testing."""
    pm = pretty_midi.PrettyMIDI(initial_tempo=120)
    inst = pretty_midi.Instrument(program=33)
    inst.notes.append(pretty_midi.Note(velocity=100, pitch=40, start=0.0, end=1.0))
    pm.instruments.append(inst)
    path = str(tmp_path / "test.mid")
    pm.write(path)
    return path


def _fluidsynth_available():
    try:
        subprocess.run(["fluidsynth", "--version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _soundfont_available():
    return os.path.exists("soundfonts/FluidR3_GM.sf2")


@pytest.mark.skipif(
    not _fluidsynth_available() or not _soundfont_available(),
    reason="fluidsynth or soundfont not available",
)
class TestRenderWav:
    def test_produces_wav_file(self, midi_file, tmp_path):
        wav_path = str(tmp_path / "test.wav")
        render_wav(midi_file, wav_path, "soundfonts/FluidR3_GM.sf2")
        assert os.path.exists(wav_path)
        assert os.path.getsize(wav_path) > 0

    def test_raises_on_missing_midi(self, tmp_path):
        wav_path = str(tmp_path / "test.wav")
        with pytest.raises(FileNotFoundError):
            render_wav("/nonexistent/file.mid", wav_path, "soundfonts/FluidR3_GM.sf2")

    def test_raises_on_missing_soundfont(self, midi_file, tmp_path):
        wav_path = str(tmp_path / "test.wav")
        with pytest.raises(FileNotFoundError):
            render_wav(midi_file, wav_path, "/nonexistent/soundfont.sf2")
