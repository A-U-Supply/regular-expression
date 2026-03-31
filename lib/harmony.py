"""Chord voicings, progressions, clusters, chromatic mediants, pedal points."""

import pretty_midi

# Note name to pitch class (C=0)
_NOTE_TO_PC = {
    "C": 0, "C#": 1, "Db": 1,
    "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6,
    "G": 7, "G#": 8, "Ab": 8,
    "A": 9, "A#": 10, "Bb": 10,
    "B": 11,
}

# Chord quality intervals (semitones from root)
_QUALITY_INTERVALS = {
    "min": [0, 3, 7],
    "min7": [0, 3, 7, 10],
    "maj7": [0, 4, 7, 11],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "add9": [0, 3, 7, 14],
    "dim": [0, 3, 6],
    "aug": [0, 4, 8],
    "power": [0, 7],
}

# Roman numeral -> (semitone offset from key root, quality)
_MINOR_NUMERALS = {
    "i": (0, "min"),
    "ii": (2, "dim"),
    "III": (3, "min"),
    "iv": (5, "min"),
    "v": (7, "min"),
    "VI": (8, "min"),
    "VII": (10, "min"),
    "IV": (5, "min"),
    "V": (7, "min"),
}


def chord(
    root: str,
    quality: str,
    octave: int = 3,
    voicing: str = "open",
) -> list[int]:
    """Build a chord as MIDI pitch numbers."""
    pc = _NOTE_TO_PC[root]
    base_pitch = pc + (octave + 1) * 12
    intervals = _QUALITY_INTERVALS[quality]

    if voicing == "closed" or quality == "power":
        return [base_pitch + iv for iv in intervals]

    # Open voicing: root in base octave, spread upper tones across higher octaves
    pitches = [base_pitch + intervals[0]]
    for i, iv in enumerate(intervals[1:], 1):
        octave_bump = 12 * (1 + (i - 1) // 2)
        pitches.append(base_pitch + iv + octave_bump)
    return pitches


def progression(
    key: str,
    numerals: list[str],
    bars: int,
    time_sig: tuple[int, int],
) -> list[list[int]]:
    """Generate chord pitch lists from Roman numeral progression."""
    root_name = key.rstrip("m")
    root_pc = _NOTE_TO_PC[root_name]

    result = []
    for numeral in numerals:
        offset, default_quality = _MINOR_NUMERALS[numeral]
        chord_pc = (root_pc + offset) % 12
        chord_name = next(name for name, pc in _NOTE_TO_PC.items() if pc == chord_pc and len(name) <= 2)
        if numeral[0].isupper():
            quality = "min"
        else:
            quality = default_quality if default_quality != "dim" else "min"
        pitches = chord(chord_name, quality, octave=2, voicing="open")
        result.append(pitches)
    return result


def cluster(center_pitch: int, width: int = 2) -> list[int]:
    """Adjacent semitones around center_pitch for harmonic crush."""
    return list(range(center_pitch - width, center_pitch + width + 1))


def chromatic_mediant(root_pitch: int, direction: str) -> int:
    """Jump to a chromatic mediant. Returns the new root pitch."""
    offsets = {
        "major_up": 4,
        "major_down": -4,
        "minor_up": 3,
        "minor_down": -3,
    }
    return root_pitch + offsets[direction]


def pedal_point(pitch: int, duration: float, velocity: int = 50) -> pretty_midi.Note:
    """A single sustained note for the given duration."""
    return pretty_midi.Note(velocity=velocity, pitch=pitch, start=0.0, end=duration)
