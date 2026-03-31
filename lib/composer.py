"""Composer class — thin plumbing layer for MIDI creation and output."""

import os
import pretty_midi
from lib.constants import TRACK_DURATION, DRUM_CHANNEL


class Composer:
    """Manages PrettyMIDI object creation, instruments, and file output."""

    def __init__(
        self,
        track_number: int,
        title: str,
        key: str,
        tempo: float,
        time_sig: tuple[int, int],
        seed: int | None = None,
    ):
        self.track_number = track_number
        self.title = title
        self.key = key
        self.tempo = tempo
        self.time_sig = time_sig
        self.seed = seed if seed is not None else track_number
        self.midi = pretty_midi.PrettyMIDI(initial_tempo=tempo)

    @property
    def duration(self) -> float:
        return TRACK_DURATION

    @property
    def beat_duration(self) -> float:
        """Duration of one beat in seconds."""
        return 60.0 / self.tempo

    @property
    def bar_duration(self) -> float:
        """Duration of one bar in seconds."""
        num, denom = self.time_sig
        if denom == 4:
            return num * self.beat_duration
        elif denom == 8:
            return num * (self.beat_duration / 2.0)
        else:
            return num * self.beat_duration

    @property
    def bars(self) -> int:
        """Number of complete bars that fit in 30 seconds."""
        return int(self.duration / self.bar_duration)

    @property
    def filename(self) -> str:
        safe_title = self.title.replace(" ", "_")
        return f"{self.track_number:02d}_{safe_title}.mid"

    def add_instrument(
        self,
        name: str,
        program: int,
        channel: int | None = None,
    ) -> pretty_midi.Instrument:
        """Add an instrument to the MIDI file and return it for note manipulation."""
        is_drum = channel == DRUM_CHANNEL
        instrument = pretty_midi.Instrument(
            program=program if not is_drum else 0,
            is_drum=is_drum,
            name=name,
        )
        self.midi.instruments.append(instrument)
        return instrument

    def write_midi(self, output_dir: str = "midi_output") -> str:
        """Write the MIDI file. Returns the output path."""
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, self.filename)
        self.midi.write(path)
        return path

    def render(self, output_dir: str = "wav_output", soundfont: str = "soundfonts/FluidR3_GM.sf2") -> str:
        """Render MIDI to WAV. Returns the output path."""
        from lib.render import render_wav
        midi_path = os.path.join("midi_output", self.filename)
        wav_filename = self.filename.replace(".mid", ".wav")
        wav_path = os.path.join(output_dir, wav_filename)
        render_wav(midi_path, wav_path, soundfont)
        return wav_path
