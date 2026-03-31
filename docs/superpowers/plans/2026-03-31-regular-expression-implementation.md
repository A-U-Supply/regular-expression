# Regular Expression Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the shared library, rendering pipeline, and project scaffolding so that individual track scripts can be composed and rendered to MIDI+WAV.

**Architecture:** Hybrid primitives + Composer pattern. Low-level music theory building blocks (`harmony`, `melody`, `bass`, `drums`, `humanize`, `directives`) return `pretty_midi.Note` lists or MIDI pitch lists. A thin `Composer` class handles PrettyMIDI object creation, instrument management, file I/O, and WAV rendering. Per-track scripts wire primitives together through the Composer.

**Tech Stack:** Python 3.10+, pretty_midi, numpy, soundfile, fluidsynth (system), uv for package management

---

## File Structure

```
regular-expression/
├── pyproject.toml
├── setup.sh
├── .gitignore
├── lib/
│   ├── __init__.py
│   ├── constants.py
│   ├── humanize.py
│   ├── harmony.py
│   ├── melody.py
│   ├── bass.py
│   ├── drums.py
│   ├── directives.py
│   ├── composer.py
│   └── render.py
├── tracks/
│   └── (empty — populated during track composition phase)
├── midi_output/
│   └── .gitkeep
├── wav_output/
│   └── .gitkeep
├── soundfonts/
│   └── (populated by setup.sh, gitignored)
├── scripts/
│   ├── render_all.py
│   └── assemble_album.py
└── tests/
    ├── __init__.py
    ├── test_constants.py
    ├── test_humanize.py
    ├── test_harmony.py
    ├── test_melody.py
    ├── test_bass.py
    ├── test_drums.py
    ├── test_directives.py
    ├── test_composer.py
    └── test_render.py
```

---

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `setup.sh`
- Create: `lib/__init__.py`
- Create: `tests/__init__.py`
- Create: `midi_output/.gitkeep`
- Create: `wav_output/.gitkeep`
- Create: `tracks/.gitkeep`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "regular-expression"
version = "0.1.0"
description = "A 34-track experimental emo MIDI album"
requires-python = ">=3.10"
dependencies = [
    "pretty-midi>=0.2.10",
    "numpy>=1.24",
    "soundfile>=0.12",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Create .gitignore**

```
soundfonts/
midi_output/*.mid
wav_output/*.wav
__pycache__/
*.pyc
.venv/
*.egg-info/
```

- [ ] **Step 3: Create setup.sh**

```bash
#!/usr/bin/env bash
set -euo pipefail

SOUNDFONT_DIR="soundfonts"
SOUNDFONT_FILE="$SOUNDFONT_DIR/FluidR3_GM.sf2"
SOUNDFONT_URL="https://keymusician01.s3.amazonaws.com/FluidR3_GM.zip"

if [ -f "$SOUNDFONT_FILE" ]; then
    echo "Soundfont already exists at $SOUNDFONT_FILE"
    exit 0
fi

mkdir -p "$SOUNDFONT_DIR"
echo "Downloading FluidR3_GM soundfont..."
curl -L -o "$SOUNDFONT_DIR/FluidR3_GM.zip" "$SOUNDFONT_URL"
unzip -o "$SOUNDFONT_DIR/FluidR3_GM.zip" -d "$SOUNDFONT_DIR"
rm "$SOUNDFONT_DIR/FluidR3_GM.zip"
echo "Soundfont installed at $SOUNDFONT_FILE"
```

- [ ] **Step 4: Create empty init files and .gitkeep files**

Create empty `lib/__init__.py`, `tests/__init__.py`, `midi_output/.gitkeep`, `wav_output/.gitkeep`, `tracks/.gitkeep`.

- [ ] **Step 5: Install dependencies and verify**

Run: `chmod +x setup.sh && uv sync`
Expected: lockfile created, dependencies installed

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml .gitignore setup.sh lib/__init__.py tests/__init__.py midi_output/.gitkeep wav_output/.gitkeep tracks/.gitkeep
git commit -m "feat: project scaffolding with deps and setup script"
```

---

### Task 2: Constants Module

**Files:**
- Create: `lib/constants.py`
- Create: `tests/test_constants.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_constants.py
from lib.constants import (
    BASS_FINGER, BASS_PICK,
    GUITAR_OVERDRIVE, GUITAR_DISTORTION, GUITAR_CLEAN,
    LEAD_SQUARE, PAD_WARM,
    DRUM_CHANNEL,
    KICK, RIM, SNARE, HAT_CLOSED, FLOOR_TOM, HAT_OPEN, RACK_TOM, CRASH, RIDE,
    SCALES, KEY_PALETTE,
    VEL_WHISPER, VEL_QUIET, VEL_NORMAL, VEL_LOUD, VEL_MAX,
    TRACK_DURATION,
)


def test_gm_programs():
    assert BASS_FINGER == 33
    assert BASS_PICK == 34
    assert GUITAR_OVERDRIVE == 29
    assert GUITAR_DISTORTION == 30
    assert GUITAR_CLEAN == 27
    assert LEAD_SQUARE == 81
    assert PAD_WARM == 89


def test_drum_channel():
    assert DRUM_CHANNEL == 9  # 0-indexed in pretty_midi


def test_drum_map():
    assert KICK == 36
    assert RIM == 37
    assert SNARE == 38
    assert HAT_CLOSED == 42
    assert FLOOR_TOM == 43
    assert HAT_OPEN == 46
    assert RACK_TOM == 47
    assert CRASH == 49
    assert RIDE == 51


def test_scales():
    # Natural minor: W-H-W-W-H-W-W (semitone intervals from root)
    assert SCALES["natural_minor"] == [0, 2, 3, 5, 7, 8, 10]
    # Phrygian: H-W-W-W-H-W-W
    assert SCALES["phrygian"] == [0, 1, 3, 5, 7, 8, 10]
    # Dorian: W-H-W-W-W-H-W
    assert SCALES["dorian"] == [0, 2, 3, 5, 7, 9, 10]
    # Chromatic
    assert SCALES["chromatic"] == list(range(12))


def test_key_palette():
    # Keys as MIDI root notes (A=57, E=52, B=59, D=50, F#=54)
    assert KEY_PALETTE == {"Am": 57, "Em": 52, "Bm": 59, "Dm": 50, "F#m": 54}


def test_velocity_ranges():
    assert VEL_WHISPER == (20, 40)
    assert VEL_QUIET == (40, 60)
    assert VEL_NORMAL == (70, 100)
    assert VEL_LOUD == (100, 120)
    assert VEL_MAX == (120, 127)


def test_track_duration():
    assert TRACK_DURATION == 30.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_constants.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Write implementation**

```python
# lib/constants.py
"""GM mappings, scale definitions, key palette, velocity ranges."""

# GM instrument programs
BASS_FINGER = 33
BASS_PICK = 34
GUITAR_OVERDRIVE = 29
GUITAR_DISTORTION = 30
GUITAR_CLEAN = 27
LEAD_SQUARE = 81
PAD_WARM = 89

# Drums use channel 9 (0-indexed in pretty_midi, = channel 10 in GM)
DRUM_CHANNEL = 9

# GM drum map
KICK = 36
RIM = 37
SNARE = 38
HAT_CLOSED = 42
FLOOR_TOM = 43
HAT_OPEN = 46
RACK_TOM = 47
CRASH = 49
RIDE = 51

# Scale intervals (semitones from root)
SCALES = {
    "natural_minor": [0, 2, 3, 5, 7, 8, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "chromatic": list(range(12)),
}

# Emo key palette — MIDI note numbers for root (octave 3, middle range)
KEY_PALETTE = {
    "Am": 57,   # A3
    "Em": 52,   # E3
    "Bm": 59,   # B3
    "Dm": 50,   # D3
    "F#m": 54,  # F#3
}

# Velocity ranges as (min, max) tuples
VEL_WHISPER = (20, 40)
VEL_QUIET = (40, 60)
VEL_NORMAL = (70, 100)
VEL_LOUD = (100, 120)
VEL_MAX = (120, 127)

# Every track is exactly 30 seconds
TRACK_DURATION = 30.0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_constants.py -v`
Expected: all 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add lib/constants.py tests/test_constants.py
git commit -m "feat: constants module with GM mappings, scales, keys, velocity ranges"
```

---

### Task 3: Humanize Module

**Files:**
- Create: `lib/humanize.py`
- Create: `tests/test_humanize.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_humanize.py
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
            # Start should be offset but within spread
            assert abs(hum.start - orig.start) <= 0.010
            # Pitch and velocity unchanged
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
        # Not all the same
        assert len(set(velocities)) > 1
        # All within valid MIDI range
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
        # Sorted by pitch ascending, each progressively later
        assert starts[0] < starts[1] < starts[2]
        # Total spread within bounds
        assert starts[-1] - starts[0] <= 0.020

    def test_up_strum_highest_first(self):
        notes = [
            pretty_midi.Note(velocity=100, pitch=40, start=1.0, end=2.0),
            pretty_midi.Note(velocity=100, pitch=52, start=1.0, end=2.0),
            pretty_midi.Note(velocity=100, pitch=64, start=1.0, end=2.0),
        ]
        result = strum(notes, direction="up", spread_ms=20)
        starts = [n.start for n in result]
        # Sorted by pitch descending, each progressively later
        assert starts[2] < starts[1] < starts[0]


class TestGhostNotes:
    def test_inserts_ghost_notes(self):
        notes = _make_notes(4, step=0.5, vel=100)
        result = ghost_notes(notes, probability=1.0, vel_range=(15, 40), seed=42)
        # Should have more notes than the original
        assert len(result) > len(notes)
        # Ghost notes have low velocity
        originals = set((n.start, n.pitch) for n in notes)
        for n in result:
            if (n.start, n.pitch) not in originals:
                assert 15 <= n.velocity <= 40

    def test_probability_zero_no_ghosts(self):
        notes = _make_notes(4, step=0.5, vel=100)
        result = ghost_notes(notes, probability=0.0, vel_range=(15, 40), seed=42)
        assert len(result) == len(notes)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_humanize.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Write implementation**

```python
# lib/humanize.py
"""Seed-controlled humanization: timing offsets, velocity variation, strum, ghost notes."""

import pretty_midi
import numpy as np


class SeededRng:
    """Deterministic RNG wrapper for reproducible humanization."""

    def __init__(self, seed: int):
        self._rng = np.random.default_rng(seed)

    def uniform(self, low: float, high: float) -> float:
        return float(self._rng.uniform(low, high))

    def randint(self, low: int, high: int) -> int:
        return int(self._rng.integers(low, high + 1))

    def random(self) -> float:
        return float(self._rng.random())


def humanize_timing(
    notes: list[pretty_midi.Note],
    spread_ms: float = 10,
    seed: int = 0,
) -> list[pretty_midi.Note]:
    """Offset note start times by +/-spread_ms. Returns new note list."""
    rng = SeededRng(seed)
    spread_s = spread_ms / 1000.0
    result = []
    for n in notes:
        offset = rng.uniform(-spread_s, spread_s)
        new_start = max(0.0, n.start + offset)
        new_end = new_start + (n.end - n.start)
        result.append(pretty_midi.Note(
            velocity=n.velocity, pitch=n.pitch, start=new_start, end=new_end,
        ))
    return result


def humanize_velocity(
    notes: list[pretty_midi.Note],
    spread: int = 15,
    seed: int = 0,
) -> list[pretty_midi.Note]:
    """Vary note velocities by +/-spread, clamped to 1-127. Returns new note list."""
    rng = SeededRng(seed)
    result = []
    for n in notes:
        offset = rng.randint(-spread, spread)
        new_vel = max(1, min(127, n.velocity + offset))
        result.append(pretty_midi.Note(
            velocity=new_vel, pitch=n.pitch, start=n.start, end=n.end,
        ))
    return result


def strum(
    notes: list[pretty_midi.Note],
    direction: str = "down",
    spread_ms: float = 20,
) -> list[pretty_midi.Note]:
    """Stagger chord tones to simulate strumming. Down = lowest pitch first."""
    sorted_notes = sorted(notes, key=lambda n: n.pitch)
    if direction == "up":
        sorted_notes = list(reversed(sorted_notes))
    count = len(sorted_notes)
    if count <= 1:
        return list(notes)
    spread_s = spread_ms / 1000.0
    step = spread_s / (count - 1)
    result = []
    for i, n in enumerate(sorted_notes):
        new_start = n.start + i * step
        new_end = new_start + (n.end - n.start)
        result.append(pretty_midi.Note(
            velocity=n.velocity, pitch=n.pitch, start=new_start, end=new_end,
        ))
    return result


def ghost_notes(
    notes: list[pretty_midi.Note],
    probability: float = 0.3,
    vel_range: tuple[int, int] = (15, 40),
    seed: int = 0,
) -> list[pretty_midi.Note]:
    """Insert low-velocity ghost notes between main hits."""
    rng = SeededRng(seed)
    result = list(notes)
    sorted_notes = sorted(notes, key=lambda n: n.start)
    ghosts = []
    for i in range(len(sorted_notes) - 1):
        if rng.random() < probability:
            curr = sorted_notes[i]
            nxt = sorted_notes[i + 1]
            ghost_start = (curr.start + nxt.start) / 2.0
            ghost_dur = min(0.05, (nxt.start - curr.start) / 4.0)
            ghosts.append(pretty_midi.Note(
                velocity=rng.randint(vel_range[0], vel_range[1]),
                pitch=curr.pitch,
                start=ghost_start,
                end=ghost_start + ghost_dur,
            ))
    result.extend(ghosts)
    return result
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_humanize.py -v`
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add lib/humanize.py tests/test_humanize.py
git commit -m "feat: humanize module with timing, velocity, strum, ghost notes"
```

---

### Task 4: Harmony Module

**Files:**
- Create: `lib/harmony.py`
- Create: `tests/test_harmony.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_harmony.py
from lib.harmony import chord, progression, cluster, chromatic_mediant, pedal_point
from lib.constants import SCALES, KEY_PALETTE
import pretty_midi


class TestChord:
    def test_minor_chord(self):
        pitches = chord("A", "min", octave=3)
        # A3=57, C4=60, E4=64
        assert 57 in pitches  # root
        assert 60 in pitches  # minor 3rd
        assert 64 in pitches  # perfect 5th

    def test_power_chord(self):
        pitches = chord("E", "power", octave=2)
        # E2=40, B2=47
        assert 40 in pitches
        assert 47 in pitches
        assert len(pitches) == 2

    def test_open_voicing_spans_octaves(self):
        pitches = chord("A", "min", octave=2, voicing="open")
        # Open voicing should span at least 2 octaves
        assert max(pitches) - min(pitches) >= 12

    def test_closed_voicing_compact(self):
        pitches = chord("A", "min", octave=3, voicing="closed")
        # Closed voicing within one octave
        assert max(pitches) - min(pitches) <= 12

    def test_sus2(self):
        pitches = chord("A", "sus2", octave=3)
        assert 57 in pitches  # root A
        assert 59 in pitches  # major 2nd (B)
        assert 64 in pitches  # perfect 5th (E)

    def test_sus4(self):
        pitches = chord("A", "sus4", octave=3)
        assert 57 in pitches  # root A
        assert 62 in pitches  # perfect 4th (D)
        assert 64 in pitches  # perfect 5th (E)

    def test_dim(self):
        pitches = chord("A", "dim", octave=3)
        assert 57 in pitches  # root
        assert 60 in pitches  # minor 3rd
        assert 63 in pitches  # diminished 5th

    def test_aug(self):
        pitches = chord("A", "aug", octave=3)
        assert 57 in pitches  # root
        assert 61 in pitches  # major 3rd
        assert 65 in pitches  # augmented 5th


class TestProgression:
    def test_returns_list_of_chord_pitch_lists(self):
        result = progression("Am", ["i", "III", "VII", "iv"], bars=4, time_sig=(4, 4))
        assert len(result) == 4
        for chord_pitches in result:
            assert isinstance(chord_pitches, list)
            assert all(isinstance(p, int) for p in chord_pitches)

    def test_i_chord_contains_root(self):
        result = progression("Am", ["i"], bars=1, time_sig=(4, 4))
        # i in Am = A minor, root A = some octave of A (pitch % 12 == 9)
        assert any(p % 12 == 9 for p in result[0])


class TestCluster:
    def test_cluster_width(self):
        pitches = cluster(60, width=2)
        # Should include 58, 59, 60, 61, 62
        assert len(pitches) == 5
        assert min(pitches) == 58
        assert max(pitches) == 62

    def test_cluster_width_1(self):
        pitches = cluster(60, width=1)
        assert len(pitches) == 3
        assert pitches == [59, 60, 61]


class TestChromaticMediant:
    def test_major_third_up(self):
        # A minor root=57 -> C# minor (major 3rd up, +4 semitones)
        new_root = chromatic_mediant(57, "major_up")
        assert new_root == 61

    def test_minor_third_down(self):
        # A (57) -> minor 3rd down = F# (54)
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_harmony.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Write implementation**

```python
# lib/harmony.py
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
# For minor key context
_MINOR_NUMERALS = {
    "i": (0, "min"),
    "ii": (2, "dim"),
    "III": (3, "min"),    # relative major, treat as minor-context chord
    "iv": (5, "min"),
    "v": (7, "min"),
    "VI": (8, "min"),     # will voice as major in context
    "VII": (10, "min"),   # will voice as major in context
    "IV": (5, "min"),     # borrowed
    "V": (7, "min"),      # borrowed
}


def chord(
    root: str,
    quality: str,
    octave: int = 3,
    voicing: str = "open",
) -> list[int]:
    """Build a chord as MIDI pitch numbers.

    Args:
        root: Note name (e.g., "A", "F#")
        quality: One of min, min7, maj7, sus2, sus4, add9, dim, aug, power
        octave: Base octave for the root
        voicing: "open" spreads across octaves, "closed" keeps compact
    """
    pc = _NOTE_TO_PC[root]
    base_pitch = pc + (octave + 1) * 12  # MIDI: C4=60, so octave+1
    intervals = _QUALITY_INTERVALS[quality]

    if voicing == "closed" or quality == "power":
        return [base_pitch + iv for iv in intervals]

    # Open voicing: root in base octave, spread upper tones across higher octaves
    pitches = [base_pitch + intervals[0]]
    for i, iv in enumerate(intervals[1:], 1):
        # Push upper tones up by 1-2 octaves
        octave_bump = 12 * (1 + (i - 1) // 2)
        pitches.append(base_pitch + iv + octave_bump)
    return pitches


def progression(
    key: str,
    numerals: list[str],
    bars: int,
    time_sig: tuple[int, int],
) -> list[list[int]]:
    """Generate chord pitch lists from Roman numeral progression.

    Returns one chord (list of pitches) per numeral. Caller handles timing.
    """
    # Extract root from key (e.g., "Am" -> "A", "F#m" -> "F#")
    root_name = key.rstrip("m")
    root_pc = _NOTE_TO_PC[root_name]

    result = []
    for numeral in numerals:
        offset, default_quality = _MINOR_NUMERALS[numeral]
        chord_pc = (root_pc + offset) % 12
        # Find the note name for this pitch class
        chord_name = next(name for name, pc in _NOTE_TO_PC.items() if pc == chord_pc and len(name) <= 2)
        # Uppercase numerals get major-like voicing, lowercase get minor
        if numeral[0].isupper():
            quality = "min"  # We still voice as minor in emo context; adjust per-track if needed
        else:
            quality = default_quality if default_quality != "dim" else "min"
        pitches = chord(chord_name, quality, octave=2, voicing="open")
        result.append(pitches)
    return result


def cluster(center_pitch: int, width: int = 2) -> list[int]:
    """Adjacent semitones around center_pitch for harmonic crush."""
    return list(range(center_pitch - width, center_pitch + width + 1))


def chromatic_mediant(root_pitch: int, direction: str) -> int:
    """Jump to a chromatic mediant. Returns the new root pitch.

    Directions: major_up (+4), major_down (-4), minor_up (+3), minor_down (-3)
    """
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_harmony.py -v`
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add lib/harmony.py tests/test_harmony.py
git commit -m "feat: harmony module with chords, progressions, clusters, mediants, pedal points"
```

---

### Task 5: Melody Module

**Files:**
- Create: `lib/melody.py`
- Create: `tests/test_melody.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_melody.py
import pretty_midi
from lib.melody import scale_pitches, contour, phrase, spike, stutter, broken_trail


class TestScalePitches:
    def test_a_natural_minor(self):
        pitches = scale_pitches("Am", "natural_minor", octave=4, num_octaves=1)
        # A4=69, B4=71, C5=72, D5=74, E5=76, F5=77, G5=79
        assert pitches == [69, 71, 72, 74, 76, 77, 79]

    def test_e_phrygian(self):
        pitches = scale_pitches("Em", "phrygian", octave=3, num_octaves=1)
        # E3=52, F3=53, G3=55, A3=57, B3=59, C4=60, D4=62
        assert pitches == [52, 53, 55, 57, 59, 60, 62]


class TestContour:
    def test_descending_stays_in_range(self):
        notes = contour("Am", "natural_minor", direction="descending", num_notes=8, octave=4, seed=42)
        assert len(notes) == 8
        for n in notes:
            assert isinstance(n, pretty_midi.Note)
        # Generally descending (first note higher than last)
        assert notes[0].pitch >= notes[-1].pitch

    def test_ascending(self):
        notes = contour("Am", "natural_minor", direction="ascending", num_notes=8, octave=4, seed=42)
        assert notes[0].pitch <= notes[-1].pitch


class TestPhrase:
    def test_returns_notes_with_gaps(self):
        notes = phrase("Am", "natural_minor", bars=4, tempo=120, time_sig=(4, 4), density=0.6, seed=42)
        assert len(notes) > 0
        # All notes within 30 seconds
        for n in notes:
            assert n.start >= 0.0
            assert n.end <= 30.5  # small tolerance for humanization

    def test_density_affects_count(self):
        sparse = phrase("Am", "natural_minor", bars=4, tempo=120, time_sig=(4, 4), density=0.3, seed=42)
        dense = phrase("Am", "natural_minor", bars=4, tempo=120, time_sig=(4, 4), density=0.9, seed=42)
        assert len(dense) > len(sparse)


class TestSpike:
    def test_spike_returns_two_notes(self):
        notes = spike(base_pitch=60, interval="min7", start=1.0, velocity=100)
        assert len(notes) == 2
        # First note is the leap up
        assert notes[0].pitch == 70  # C4 + min7 (10 semitones)
        # Second note drops back
        assert notes[1].pitch == 60

    def test_octave_spike(self):
        notes = spike(base_pitch=60, interval="octave", start=1.0, velocity=100)
        assert notes[0].pitch == 72  # C4 + 12


class TestStutter:
    def test_repeated_notes(self):
        notes = stutter(pitch=64, count=6, note_duration=0.1, gap=0.05, start=0.0, velocity=90)
        assert len(notes) == 6
        assert all(n.pitch == 64 for n in notes)
        assert all(n.velocity == 90 for n in notes)
        # Each note starts after the previous
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
        # First 2 notes at full velocity, remaining fade
        assert result[0].velocity == 100
        assert result[1].velocity == 100
        assert result[2].velocity < 100
        assert result[3].velocity < result[2].velocity
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_melody.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Write implementation**

```python
# lib/melody.py
"""Melody contour builders, phrase generators, spikes, stutters, broken trails."""

import pretty_midi
from lib.constants import SCALES, KEY_PALETTE
from lib.humanize import SeededRng

# Interval name to semitones for spike()
_SPIKE_INTERVALS = {
    "min2": 1, "maj2": 2, "min3": 3, "maj3": 4,
    "P4": 5, "tritone": 6, "P5": 7,
    "min6": 8, "maj6": 9, "min7": 10, "maj7": 11,
    "octave": 12,
}


def scale_pitches(
    key: str,
    mode: str,
    octave: int = 4,
    num_octaves: int = 1,
) -> list[int]:
    """Get MIDI pitches for a scale across octaves."""
    root_name = key.rstrip("m")
    # Note name to pitch class
    note_to_pc = {
        "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
        "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
        "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11,
    }
    root_pc = note_to_pc[root_name]
    base_midi = root_pc + (octave + 1) * 12
    intervals = SCALES[mode]
    pitches = []
    for oct in range(num_octaves):
        for iv in intervals:
            pitches.append(base_midi + iv + oct * 12)
    return pitches


def contour(
    key: str,
    mode: str,
    direction: str = "descending",
    num_notes: int = 8,
    octave: int = 4,
    seed: int = 0,
    start_time: float = 0.0,
    note_duration: float = 0.25,
    note_gap: float = 0.1,
    velocity: int = 90,
) -> list[pretty_midi.Note]:
    """Generate a melodic contour within scale constraints.

    Direction controls the general trend (descending/ascending) but individual
    notes may move against the trend for musicality.
    """
    rng = SeededRng(seed)
    available = scale_pitches(key, mode, octave=octave, num_octaves=2)

    if direction == "descending":
        start_idx = len(available) - 1 - rng.randint(0, 3)
    else:
        start_idx = rng.randint(0, 3)

    notes = []
    idx = start_idx
    t = start_time
    for i in range(num_notes):
        pitch = available[max(0, min(idx, len(available) - 1))]
        notes.append(pretty_midi.Note(
            velocity=velocity, pitch=pitch, start=t, end=t + note_duration,
        ))
        t += note_duration + note_gap
        # Move in the general direction with occasional contrary motion
        if direction == "descending":
            step = -rng.randint(1, 2) if rng.random() < 0.75 else rng.randint(1, 2)
        else:
            step = rng.randint(1, 2) if rng.random() < 0.75 else -rng.randint(1, 2)
        idx += step
    return notes


def phrase(
    key: str,
    mode: str,
    bars: int,
    tempo: float,
    time_sig: tuple[int, int],
    density: float = 0.6,
    seed: int = 0,
    velocity: int = 90,
) -> list[pretty_midi.Note]:
    """Generate an asymmetric melodic phrase with gaps.

    density: 0.0-1.0, controls how many beats get notes vs rests.
    """
    rng = SeededRng(seed)
    available = scale_pitches(key, mode, octave=4, num_octaves=2)
    beats_per_bar = time_sig[0]
    beat_duration = 60.0 / tempo
    total_beats = bars * beats_per_bar

    notes = []
    idx = len(available) // 2  # start middle of range
    t = 0.0
    for beat in range(total_beats):
        t = beat * beat_duration
        if rng.random() > density:
            continue  # rest
        pitch = available[max(0, min(idx, len(available) - 1))]
        dur = beat_duration * rng.uniform(0.4, 0.9)
        vel = max(1, min(127, velocity + rng.randint(-20, 20)))
        notes.append(pretty_midi.Note(velocity=vel, pitch=pitch, start=t, end=t + dur))
        idx += rng.randint(-2, 2)
    return notes


def spike(
    base_pitch: int,
    interval: str = "min7",
    start: float = 0.0,
    velocity: int = 100,
    leap_duration: float = 0.15,
    drop_duration: float = 0.3,
) -> list[pretty_midi.Note]:
    """Leap up by interval then immediate drop back to base. Returns 2 notes."""
    semitones = _SPIKE_INTERVALS[interval]
    high_pitch = base_pitch + semitones
    return [
        pretty_midi.Note(velocity=velocity, pitch=high_pitch, start=start, end=start + leap_duration),
        pretty_midi.Note(velocity=velocity, pitch=base_pitch, start=start + leap_duration, end=start + leap_duration + drop_duration),
    ]


def stutter(
    pitch: int,
    count: int,
    note_duration: float = 0.1,
    gap: float = 0.05,
    start: float = 0.0,
    velocity: int = 90,
) -> list[pretty_midi.Note]:
    """Obsessive single-note repetition."""
    notes = []
    t = start
    for _ in range(count):
        notes.append(pretty_midi.Note(velocity=velocity, pitch=pitch, start=t, end=t + note_duration))
        t += note_duration + gap
    return notes


def broken_trail(
    notes: list[pretty_midi.Note],
    decay_point: int,
) -> list[pretty_midi.Note]:
    """Phrase that trails into nothing. Notes after decay_point fade in velocity."""
    result = []
    remaining = len(notes) - decay_point
    for i, n in enumerate(notes):
        if i < decay_point:
            result.append(pretty_midi.Note(velocity=n.velocity, pitch=n.pitch, start=n.start, end=n.end))
        else:
            fade = max(1, int(n.velocity * (1.0 - (i - decay_point + 1) / (remaining + 1))))
            result.append(pretty_midi.Note(velocity=fade, pitch=n.pitch, start=n.start, end=n.end))
    return result
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_melody.py -v`
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add lib/melody.py tests/test_melody.py
git commit -m "feat: melody module with contours, phrases, spikes, stutters, broken trails"
```

---

### Task 6: Bass Module

**Files:**
- Create: `lib/bass.py`
- Create: `tests/test_bass.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_bass.py
import pretty_midi
from lib.bass import locked_bass, driving_eighths, counter_melody, chromatic_approach


class TestLockedBass:
    def test_returns_notes(self):
        # Simulate a kick pattern: hits at beats 1 and 3 in 4/4 at 120bpm
        kick_times = [0.0, 1.0, 2.0, 3.0]  # 4 bars worth of kick on beat 1
        notes = locked_bass(kick_times, root=40, fifth=47, bars=4, tempo=120, seed=42)
        assert len(notes) > 0
        for n in notes:
            assert isinstance(n, pretty_midi.Note)
            assert n.pitch in (40, 47, 52)  # root, fifth, or octave

    def test_some_notes_align_with_kicks(self):
        kick_times = [0.0, 0.5, 1.0, 1.5]
        notes = locked_bass(kick_times, root=40, fifth=47, bars=2, tempo=120, seed=42)
        note_starts = {round(n.start, 2) for n in notes}
        kick_set = {round(t, 2) for t in kick_times}
        # At least some overlap
        assert len(note_starts & kick_set) > 0


class TestDrivingEighths:
    def test_note_count(self):
        # 2 bars of 4/4 at 120bpm = 2 * 4 * 2 = 16 eighth notes
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
            # At least one interval >= 7 semitones (P5 or wider)
            assert any(iv >= 7 for iv in intervals)


class TestChromaticApproach:
    def test_ascending(self):
        notes = chromatic_approach(target=40, direction="up", length=4, start=0.0, note_duration=0.2)
        assert len(notes) == 4
        # Last note should be the target
        assert notes[-1].pitch == 40
        # Notes should ascend chromatically
        for i in range(len(notes) - 1):
            assert notes[i + 1].pitch == notes[i].pitch + 1

    def test_descending(self):
        notes = chromatic_approach(target=40, direction="down", length=3, start=0.0, note_duration=0.2)
        assert len(notes) == 3
        assert notes[-1].pitch == 40
        for i in range(len(notes) - 1):
            assert notes[i + 1].pitch == notes[i].pitch - 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_bass.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Write implementation**

```python
# lib/bass.py
"""Bass line builders: kick-locked, driving eighths, counter-melody, chromatic approaches."""

import pretty_midi
from lib.melody import scale_pitches
from lib.humanize import SeededRng


def locked_bass(
    kick_times: list[float],
    root: int,
    fifth: int,
    bars: int,
    tempo: float,
    seed: int = 0,
    velocity: int = 100,
) -> list[pretty_midi.Note]:
    """Bass that follows kick ~60% of the time, drifts the other 40%.

    Args:
        kick_times: List of kick hit times in seconds.
        root: MIDI pitch of the root note.
        fifth: MIDI pitch of the fifth.
        bars: Number of bars.
        tempo: BPM.
    """
    rng = SeededRng(seed)
    beat_dur = 60.0 / tempo
    octave_up = root + 12
    pitch_options = [root, fifth, octave_up]
    notes = []

    for kt in kick_times:
        if rng.random() < 0.6:
            # Lock with kick
            pitch = root if rng.random() < 0.7 else fifth
            dur = beat_dur * rng.uniform(0.4, 0.8)
            vel = max(1, min(127, velocity + rng.randint(-10, 10)))
            notes.append(pretty_midi.Note(velocity=vel, pitch=pitch, start=kt, end=kt + dur))
        else:
            # Drift: anticipate or drag
            offset = rng.uniform(-beat_dur * 0.2, beat_dur * 0.3)
            start = max(0.0, kt + offset)
            pitch = pitch_options[rng.randint(0, len(pitch_options) - 1)]
            dur = beat_dur * rng.uniform(0.3, 0.9)
            vel = max(1, min(127, velocity + rng.randint(-15, 10)))
            notes.append(pretty_midi.Note(velocity=vel, pitch=pitch, start=start, end=start + dur))
    return notes


def driving_eighths(
    root: int,
    bars: int,
    tempo: float,
    time_sig: tuple[int, int] = (4, 4),
    velocity: int = 110,
) -> list[pretty_midi.Note]:
    """Repeated eighth notes on one pitch. Wall of sound."""
    eighth_dur = 60.0 / tempo / 2.0
    total_eighths = bars * time_sig[0] * 2
    notes = []
    for i in range(total_eighths):
        start = i * eighth_dur
        notes.append(pretty_midi.Note(
            velocity=velocity, pitch=root, start=start, end=start + eighth_dur * 0.9,
        ))
    return notes


def counter_melody(
    key: str,
    mode: str,
    bars: int,
    tempo: float,
    time_sig: tuple[int, int] = (4, 4),
    seed: int = 0,
    velocity: int = 90,
) -> list[pretty_midi.Note]:
    """Wide-interval bass melody using min7, octave, tritone leaps."""
    rng = SeededRng(seed)
    available = scale_pitches(key, mode, octave=2, num_octaves=2)
    beat_dur = 60.0 / tempo
    total_beats = bars * time_sig[0]
    wide_intervals = [6, 7, 10, 12]  # tritone, P5, min7, octave in scale steps approx

    notes = []
    idx = len(available) // 2
    t = 0.0
    for beat in range(total_beats):
        t = beat * beat_dur
        if rng.random() < 0.15:
            continue  # occasional rest
        pitch = available[max(0, min(idx, len(available) - 1))]
        dur = beat_dur * rng.uniform(0.5, 0.95)
        vel = max(1, min(127, velocity + rng.randint(-15, 15)))
        notes.append(pretty_midi.Note(velocity=vel, pitch=pitch, start=t, end=t + dur))
        # Jump by a wide interval
        jump = wide_intervals[rng.randint(0, len(wide_intervals) - 1)]
        if rng.random() < 0.5:
            jump = -jump
        idx += jump
    return notes


def chromatic_approach(
    target: int,
    direction: str = "up",
    length: int = 4,
    start: float = 0.0,
    note_duration: float = 0.2,
    velocity: int = 100,
) -> list[pretty_midi.Note]:
    """Half-step slide into target pitch.

    direction "up" = ascending into target, "down" = descending into target.
    """
    notes = []
    if direction == "up":
        first_pitch = target - length + 1
        for i in range(length):
            pitch = first_pitch + i
            t = start + i * note_duration
            notes.append(pretty_midi.Note(velocity=velocity, pitch=pitch, start=t, end=t + note_duration))
    else:
        first_pitch = target + length - 1
        for i in range(length):
            pitch = first_pitch - i
            t = start + i * note_duration
            notes.append(pretty_midi.Note(velocity=velocity, pitch=pitch, start=t, end=t + note_duration))
    return notes
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_bass.py -v`
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add lib/bass.py tests/test_bass.py
git commit -m "feat: bass module with locked bass, driving eighths, counter melody, chromatic approach"
```

---

### Task 7: Drums Module

**Files:**
- Create: `lib/drums.py`
- Create: `tests/test_drums.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_drums.py
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
        # Should have kicks near beat 1 (0.0) and beat 3 (1.0)
        assert any(abs(t - 0.0) < 0.02 for t in kick_starts)
        assert any(abs(t - beat_dur * 2) < 0.02 for t in kick_starts)


class TestBlast:
    def test_alternating_kick_snare(self):
        notes = blast(bars=1, tempo=120, time_sig=(4, 4), seed=42)
        # 16th notes in 1 bar of 4/4 = 16 notes, alternating kick/snare
        kick_snare = [n for n in notes if n.pitch in (KICK, SNARE)]
        assert len(kick_snare) >= 14  # some may be ghost-noted

    def test_capped_at_4_bars(self):
        notes_4 = blast(bars=4, tempo=120, time_sig=(4, 4), seed=42)
        notes_8 = blast(bars=8, tempo=120, time_sig=(4, 4), seed=42)
        # 8 bars should be capped to 4 bars worth
        max_time_4 = max(n.end for n in notes_4)
        max_time_8 = max(n.end for n in notes_8)
        assert abs(max_time_4 - max_time_8) < 0.1


class TestHalfTime:
    def test_snare_on_beat_3(self):
        notes = half_time(bars=2, tempo=120, time_sig=(4, 4), seed=42)
        snare_notes = [n for n in notes if n.pitch == SNARE]
        beat_dur = 60.0 / 120
        # Snare on beat 3 of each bar (time = 2 * beat_dur from bar start)
        for sn in snare_notes:
            # Beat 3 of some bar
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
        # All within roughly 1 beat duration
        max_time = max(n.end for n in notes)
        beat_dur = 60.0 / 120
        assert max_time <= beat_dur * 1.5  # small tolerance

    def test_uses_toms_or_snare(self):
        notes = fill(beats=2, tempo=120, seed=42)
        pitches = {n.pitch for n in notes}
        fill_instruments = {SNARE, FLOOR_TOM, RACK_TOM}
        assert len(pitches & fill_instruments) > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_drums.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Write implementation**

```python
# lib/drums.py
"""Drum pattern builders with humanized timing."""

import pretty_midi
from lib.constants import (
    KICK, SNARE, HAT_CLOSED, HAT_OPEN, FLOOR_TOM, RACK_TOM, CRASH,
)
from lib.humanize import SeededRng


def _drum_note(pitch: int, start: float, duration: float = 0.1, velocity: int = 100) -> pretty_midi.Note:
    return pretty_midi.Note(velocity=velocity, pitch=pitch, start=start, end=start + duration)


def driving_emo(
    bars: int,
    tempo: float,
    time_sig: tuple[int, int] = (4, 4),
    seed: int = 0,
) -> list[pretty_midi.Note]:
    """Kick 1+3, snare 2+4, 8th-note hats. Humanized timing and velocity."""
    rng = SeededRng(seed)
    beat_dur = 60.0 / tempo
    eighth = beat_dur / 2.0
    beats_per_bar = time_sig[0]
    notes = []

    for bar in range(bars):
        bar_start = bar * beats_per_bar * beat_dur
        for beat in range(beats_per_bar):
            t = bar_start + beat * beat_dur
            # Kick on 1 and 3 (0-indexed: 0, 2)
            if beat % 2 == 0:
                offset = rng.uniform(-0.005, 0.005)
                notes.append(_drum_note(KICK, max(0.0, t + offset), velocity=100 + rng.randint(-8, 8)))
            # Snare on 2 and 4 (0-indexed: 1, 3)
            if beat % 2 == 1:
                offset = rng.uniform(-0.005, 0.005)
                notes.append(_drum_note(SNARE, max(0.0, t + offset), velocity=100 + rng.randint(-8, 8)))
                # Ghost snare before main hit sometimes
                if rng.random() < 0.3:
                    ghost_t = max(0.0, t - eighth * 0.5 + rng.uniform(-0.005, 0.005))
                    notes.append(_drum_note(SNARE, ghost_t, velocity=rng.randint(15, 35)))
            # 8th note hats
            for sub in range(2):
                ht = t + sub * eighth + rng.uniform(-0.005, 0.005)
                hat_vel = rng.randint(50, 110)
                hat_pitch = HAT_OPEN if (sub == 1 and rng.random() < 0.2) else HAT_CLOSED
                notes.append(_drum_note(hat_pitch, max(0.0, ht), velocity=hat_vel))
    return notes


def blast(
    bars: int,
    tempo: float,
    time_sig: tuple[int, int] = (4, 4),
    seed: int = 0,
) -> list[pretty_midi.Note]:
    """Kick+snare alternating on 16ths. Capped at 4 bars."""
    rng = SeededRng(seed)
    bars = min(bars, 4)
    sixteenth = 60.0 / tempo / 4.0
    beats_per_bar = time_sig[0]
    total_sixteenths = bars * beats_per_bar * 4
    notes = []

    for i in range(total_sixteenths):
        t = i * sixteenth + rng.uniform(-0.005, 0.005)
        t = max(0.0, t)
        vel = 100 + rng.randint(-10, 10)
        if i % 2 == 0:
            notes.append(_drum_note(KICK, t, velocity=vel))
        else:
            notes.append(_drum_note(SNARE, t, velocity=vel))
    return notes


def half_time(
    bars: int,
    tempo: float,
    time_sig: tuple[int, int] = (4, 4),
    seed: int = 0,
) -> list[pretty_midi.Note]:
    """Snare on beat 3 only. Cavernous."""
    rng = SeededRng(seed)
    beat_dur = 60.0 / tempo
    beats_per_bar = time_sig[0]
    notes = []

    for bar in range(bars):
        bar_start = bar * beats_per_bar * beat_dur
        for beat in range(beats_per_bar):
            t = bar_start + beat * beat_dur
            # Kick on beat 1
            if beat == 0:
                offset = rng.uniform(-0.005, 0.005)
                notes.append(_drum_note(KICK, max(0.0, t + offset), velocity=100 + rng.randint(-8, 8)))
            # Snare on beat 3 only (0-indexed: 2)
            if beat == 2:
                offset = rng.uniform(-0.005, 0.005)
                notes.append(_drum_note(SNARE, max(0.0, t + offset), velocity=110 + rng.randint(-5, 5)))
            # Sparse hats
            if rng.random() < 0.6:
                offset = rng.uniform(-0.005, 0.005)
                notes.append(_drum_note(HAT_CLOSED, max(0.0, t + offset), velocity=rng.randint(40, 80)))
    return notes


def floor_tom_pulse(
    bars: int,
    tempo: float,
    time_sig: tuple[int, int] = (4, 4),
    seed: int = 0,
) -> list[pretty_midi.Note]:
    """Floor tom replaces kick. No kick in this pattern."""
    rng = SeededRng(seed)
    beat_dur = 60.0 / tempo
    beats_per_bar = time_sig[0]
    notes = []

    for bar in range(bars):
        bar_start = bar * beats_per_bar * beat_dur
        for beat in range(beats_per_bar):
            t = bar_start + beat * beat_dur
            # Floor tom on 1 and 3
            if beat % 2 == 0:
                offset = rng.uniform(-0.005, 0.005)
                notes.append(_drum_note(FLOOR_TOM, max(0.0, t + offset), velocity=95 + rng.randint(-10, 10)))
            # Hat on every beat
            offset = rng.uniform(-0.005, 0.005)
            notes.append(_drum_note(HAT_CLOSED, max(0.0, t + offset), velocity=rng.randint(50, 90)))
    return notes


def no_snare(
    bars: int,
    tempo: float,
    time_sig: tuple[int, int] = (4, 4),
    seed: int = 0,
) -> list[pretty_midi.Note]:
    """Kick, hat, toms only. Anxious."""
    rng = SeededRng(seed)
    beat_dur = 60.0 / tempo
    eighth = beat_dur / 2.0
    beats_per_bar = time_sig[0]
    notes = []

    for bar in range(bars):
        bar_start = bar * beats_per_bar * beat_dur
        for beat in range(beats_per_bar):
            t = bar_start + beat * beat_dur
            # Kick on 1 and 3
            if beat % 2 == 0:
                offset = rng.uniform(-0.005, 0.005)
                notes.append(_drum_note(KICK, max(0.0, t + offset), velocity=95 + rng.randint(-8, 8)))
            # Rack tom on some beats
            if rng.random() < 0.3:
                offset = rng.uniform(-0.005, 0.005)
                notes.append(_drum_note(RACK_TOM, max(0.0, t + offset), velocity=rng.randint(60, 90)))
            # 8th hats
            for sub in range(2):
                ht = t + sub * eighth + rng.uniform(-0.005, 0.005)
                notes.append(_drum_note(HAT_CLOSED, max(0.0, ht), velocity=rng.randint(50, 100)))
    return notes


def fill(
    beats: int = 1,
    tempo: float = 120,
    seed: int = 0,
    start: float = 0.0,
) -> list[pretty_midi.Note]:
    """Short stumbling fill using toms and snare."""
    rng = SeededRng(seed)
    beat_dur = 60.0 / tempo
    sixteenth = beat_dur / 4.0
    total_sixteenths = beats * 4
    fill_instruments = [SNARE, FLOOR_TOM, RACK_TOM]
    notes = []

    for i in range(total_sixteenths):
        if rng.random() < 0.3:
            continue  # gap for stumbling feel
        t = start + i * sixteenth + rng.uniform(-0.008, 0.008)
        pitch = fill_instruments[rng.randint(0, len(fill_instruments) - 1)]
        vel = rng.randint(70, 110)
        notes.append(_drum_note(pitch, max(0.0, t), velocity=vel))
    return notes
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_drums.py -v`
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add lib/drums.py tests/test_drums.py
git commit -m "feat: drums module with driving emo, blast, half-time, floor tom, no-snare, fills"
```

---

### Task 8: Directives Module

**Files:**
- Create: `lib/directives.py`
- Create: `tests/test_directives.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_directives.py
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
        # Should have 4 groups of notes
        assert len(result) == 4
        # First repetition is unmodified
        assert len(result[0]) == 3
        assert all(r.pitch == o.pitch for r, o in zip(result[0], base_notes))
        # Later repetitions should differ
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
        # Each boundary is (start_bar, end_bar)
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
            assert n.pitch == 60 or n.pitch == 60 + 12 or n.pitch == 60 - 12  # unison/octave
            assert n.start == 5.0
            assert n.end == 7.0


class TestReverseStructurePlan:
    def test_instruments_decrease(self):
        plan = reverse_structure_plan(total_bars=16, num_instruments=4)
        # Should have sections where instruments peel off one by one
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_directives.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Write implementation**

```python
# lib/directives.py
"""Special structural directives for the album.

These return plans (bar boundaries, note lists) that track scripts use
to structure their compositions. They don't modify Composer state directly.
"""

import pretty_midi
from lib.humanize import SeededRng


def collapse_plan(
    total_bars: int,
    collapse_bar: int,
    re_entry_bar: int,
) -> dict:
    """Plan for The Collapse directive.

    Returns bar boundaries for: full ensemble, solo instrument, re-entry.
    """
    return {
        "before": (0, collapse_bar),
        "solo": (collapse_bar, re_entry_bar),
        "after": (re_entry_bar, total_bars),
    }


def loop_that_breaks(
    base_notes: list[pretty_midi.Note],
    repetitions: int = 4,
    seed: int = 0,
) -> list[list[pretty_midi.Note]]:
    """Repeat a passage with cumulative mutations.

    Returns a list of repetitions, each a list of notes. First repetition
    is unmodified; subsequent ones accumulate mutations.
    """
    rng = SeededRng(seed)
    loop_duration = max(n.end for n in base_notes) - min(n.start for n in base_notes)
    result = []

    for rep in range(repetitions):
        time_offset = rep * loop_duration
        rep_notes = []
        for n in base_notes:
            pitch = n.pitch
            start = n.start + time_offset
            end = n.end + time_offset
            vel = n.velocity

            if rep > 0:
                # Accumulate mutations based on repetition number
                for _ in range(rep):
                    mutation = rng.randint(0, 2)
                    if mutation == 0 and rng.random() < 0.3 * rep:
                        continue  # drop this note
                    elif mutation == 1:
                        pitch += rng.randint(-2, 2)  # wrong pitch
                    elif mutation == 2:
                        start += rng.uniform(-0.05, 0.05) * rep  # shift beat

            rep_notes.append(pretty_midi.Note(
                velocity=max(1, min(127, vel)),
                pitch=max(0, min(127, pitch)),
                start=max(0.0, start),
                end=max(start + 0.01, end),
            ))
        result.append(rep_notes)
    return result


def two_songs_stitched_plan(
    total_bars: int,
    split_bar: int,
    transition_bars: int = 1,
) -> dict:
    """Plan for Two Songs Stitched directive.

    Returns bar boundaries for song A, transition, and song B.
    """
    return {
        "song_a": (0, split_bar),
        "transition": (split_bar, split_bar + transition_bars),
        "song_b": (split_bar + transition_bars, total_bars),
    }


def countdown_plan(
    tempo: float,
    time_sig: tuple[int, int],
    section_bars: list[int] | None = None,
) -> dict:
    """Plan for The Countdown directive.

    Returns section bar counts and their boundaries.
    """
    if section_bars is None:
        section_bars = [8, 4, 2, 1]
    boundaries = []
    current = 0
    for bars in section_bars:
        boundaries.append((current, current + bars))
        current += bars
    return {
        "section_bars": section_bars,
        "bar_boundaries": boundaries,
    }


def unison_collapse(
    target_pitch: int,
    num_instruments: int,
    start: float,
    duration: float,
    velocity: int = 80,
) -> list[pretty_midi.Note]:
    """All instruments converge on one note/octave.

    Returns one note per instrument, at unison or octave intervals.
    """
    notes = []
    octave_offsets = [0, 0, 12, -12]  # unison, unison, octave up, octave down
    for i in range(num_instruments):
        offset = octave_offsets[i % len(octave_offsets)]
        pitch = max(0, min(127, target_pitch + offset))
        notes.append(pretty_midi.Note(
            velocity=velocity, pitch=pitch, start=start, end=start + duration,
        ))
    return notes


def reverse_structure_plan(
    total_bars: int,
    num_instruments: int,
) -> list[dict]:
    """Plan for Reverse Structure directive.

    Returns sections from full ensemble to solo, stripping one instrument per section.
    """
    bars_per_section = max(1, total_bars // num_instruments)
    plan = []
    current_bar = 0
    for i in range(num_instruments):
        remaining = num_instruments - i
        end_bar = min(current_bar + bars_per_section, total_bars)
        if i == num_instruments - 1:
            end_bar = total_bars
        plan.append({
            "bars": (current_bar, end_bar),
            "num_instruments": remaining,
        })
        current_bar = end_bar
    return plan


def rhythmic_displacement(
    notes: list[pretty_midi.Note],
    offset_eighths: int = 1,
    tempo: float = 120,
) -> list[pretty_midi.Note]:
    """Shift all notes by a number of eighth notes. Feels persistently wrong."""
    eighth_dur = 60.0 / tempo / 2.0
    offset = offset_eighths * eighth_dur
    return [
        pretty_midi.Note(
            velocity=n.velocity,
            pitch=n.pitch,
            start=max(0.0, n.start + offset),
            end=max(0.01, n.end + offset),
        )
        for n in notes
    ]


def drone(
    pitch: int,
    duration: float = 30.0,
    velocity: int = 45,
) -> pretty_midi.Note:
    """A single sustained low note for the entire track."""
    return pretty_midi.Note(velocity=velocity, pitch=pitch, start=0.0, end=duration)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_directives.py -v`
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add lib/directives.py tests/test_directives.py
git commit -m "feat: directives module with all 8 structural techniques"
```

---

### Task 9: Composer Module

**Files:**
- Create: `lib/composer.py`
- Create: `tests/test_composer.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_composer.py
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
        # Verify it's valid MIDI
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
        assert c.seed == 5  # defaults to track number

    def test_seed_override(self):
        c = Composer(5, "shit", key="Am", tempo=120, time_sig=(4, 4), seed=42)
        assert c.seed == 42

    def test_bars_property(self):
        # 120 BPM, 4/4, 30 seconds = 30 / (60/120 * 4) = 15 bars
        c = Composer(1, "wtf", key="Am", tempo=120, time_sig=(4, 4))
        assert c.bars == 15

    def test_bars_property_odd_meter(self):
        # 120 BPM, 7/8, 30 seconds. Bar = 7 * (60/120/2) = 1.75s. 30/1.75 = 17.14 -> 17
        c = Composer(1, "wtf", key="Am", tempo=120, time_sig=(7, 8))
        assert c.bars == 17

    def test_beat_duration(self):
        c = Composer(1, "wtf", key="Am", tempo=120, time_sig=(4, 4))
        assert abs(c.beat_duration - 0.5) < 0.001

    def test_bar_duration(self):
        c = Composer(1, "wtf", key="Am", tempo=120, time_sig=(4, 4))
        assert abs(c.bar_duration - 2.0) < 0.001
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_composer.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Write implementation**

```python
# lib/composer.py
"""Composer class — thin plumbing layer for MIDI creation and output."""

import os
import pretty_midi
from lib.constants import TRACK_DURATION, DRUM_CHANNEL


class Composer:
    """Manages PrettyMIDI object creation, instruments, and file output.

    Args:
        track_number: Album track number (1-34).
        title: Track title (used in filename).
        key: Key string (e.g., "Am", "F#m").
        tempo: BPM.
        time_sig: Tuple of (numerator, denominator).
        seed: RNG seed. Defaults to track_number for deterministic "album version".
    """

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
        # For x/4 time, a beat = quarter note. For x/8, a beat = eighth note.
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_composer.py -v`
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add lib/composer.py tests/test_composer.py
git commit -m "feat: composer module with MIDI plumbing, instrument management, file output"
```

---

### Task 10: Render Module

**Files:**
- Create: `lib/render.py`
- Create: `tests/test_render.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_render.py
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_render.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Write implementation**

```python
# lib/render.py
"""Fluidsynth wrapper for MIDI-to-WAV rendering."""

import os
import subprocess


def render_wav(mid_path: str, wav_path: str, soundfont_path: str) -> None:
    """Render a MIDI file to WAV using fluidsynth.

    Args:
        mid_path: Path to input .mid file.
        wav_path: Path for output .wav file.
        soundfont_path: Path to .sf2 soundfont file.

    Raises:
        FileNotFoundError: If MIDI file or soundfont doesn't exist.
        RuntimeError: If fluidsynth fails.
    """
    if not os.path.exists(mid_path):
        raise FileNotFoundError(f"MIDI file not found: {mid_path}")
    if not os.path.exists(soundfont_path):
        raise FileNotFoundError(f"Soundfont not found: {soundfont_path}")

    os.makedirs(os.path.dirname(wav_path) or ".", exist_ok=True)

    result = subprocess.run(
        [
            "fluidsynth",
            "-ni",           # non-interactive, no shell
            soundfont_path,
            mid_path,
            "-F", wav_path,  # render to file
            "-r", "44100",   # sample rate
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"fluidsynth failed: {result.stderr}")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_render.py -v`
Expected: tests PASS (or skip if fluidsynth/soundfont not installed yet)

- [ ] **Step 5: Commit**

```bash
git add lib/render.py tests/test_render.py
git commit -m "feat: render module wrapping fluidsynth for MIDI-to-WAV"
```

---

### Task 11: Scripts (render_all and assemble_album)

**Files:**
- Create: `scripts/render_all.py`
- Create: `scripts/assemble_album.py`

- [ ] **Step 1: Write render_all.py**

```python
#!/usr/bin/env python
"""Run all track scripts to generate MIDI and WAV files."""

import importlib
import sys
from pathlib import Path


def main():
    tracks_dir = Path(__file__).parent.parent / "tracks"
    track_files = sorted(tracks_dir.glob("[0-9][0-9]_*.py"))

    if not track_files:
        print("No track scripts found in tracks/")
        sys.exit(1)

    print(f"Found {len(track_files)} tracks")

    # Add project root to path so tracks can import lib
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

    for track_file in track_files:
        print(f"Generating {track_file.name}...")
        module_name = track_file.stem
        spec = importlib.util.spec_from_file_location(module_name, track_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        module.generate()
        print(f"  Done: {track_file.name}")

    print(f"\nAll {len(track_files)} tracks generated.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Write assemble_album.py**

```python
#!/usr/bin/env python
"""Concatenate all track WAVs into one album file."""

import sys
from pathlib import Path
import soundfile as sf
import numpy as np


def main():
    wav_dir = Path(__file__).parent.parent / "wav_output"
    wav_files = sorted(wav_dir.glob("[0-9][0-9]_*.wav"))

    if not wav_files:
        print("No WAV files found in wav_output/")
        sys.exit(1)

    print(f"Assembling {len(wav_files)} tracks into album...")

    chunks = []
    sample_rate = None
    for wav_file in wav_files:
        data, sr = sf.read(wav_file)
        if sample_rate is None:
            sample_rate = sr
        elif sr != sample_rate:
            print(f"Warning: {wav_file.name} has sample rate {sr}, expected {sample_rate}")
        chunks.append(data)

    album = np.concatenate(chunks)
    output_path = wav_dir / "regular_expression.wav"
    sf.write(str(output_path), album, sample_rate)
    duration = len(album) / sample_rate
    print(f"Album written to {output_path} ({duration:.1f}s)")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Verify scripts are syntactically valid**

Run: `uv run python -c "import ast; ast.parse(open('scripts/render_all.py').read()); ast.parse(open('scripts/assemble_album.py').read()); print('OK')"`
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add scripts/render_all.py scripts/assemble_album.py
git commit -m "feat: render_all and assemble_album scripts"
```

---

### Task 12: CLI Interface for Track Scripts

**Files:**
- Create: `lib/cli.py`
- Create: `tests/test_cli.py`

This is a shared CLI parser so every track script doesn't duplicate argparse boilerplate.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_cli.py
from lib.cli import parse_track_args


class TestParseTrackArgs:
    def test_defaults(self):
        args = parse_track_args([])
        assert args.seed is None
        assert args.no_render is False

    def test_seed(self):
        args = parse_track_args(["--seed", "42"])
        assert args.seed == 42

    def test_no_render(self):
        args = parse_track_args(["--no-render"])
        assert args.no_render is True
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py -v`
Expected: FAIL (ImportError)

- [ ] **Step 3: Write implementation**

```python
# lib/cli.py
"""Shared CLI parser for track scripts."""

import argparse


def parse_track_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse common track script arguments.

    Args:
        argv: Argument list. None = sys.argv[1:].
    """
    parser = argparse.ArgumentParser(description="Generate a track for Regular Expression")
    parser.add_argument("--seed", type=int, default=None, help="RNG seed for variation (default: track number)")
    parser.add_argument("--no-render", action="store_true", help="Skip WAV rendering")
    return parser.parse_args(argv)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cli.py -v`
Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add lib/cli.py tests/test_cli.py
git commit -m "feat: shared CLI parser for track scripts"
```

---

### Task 13: Integration Test — Full Pipeline Smoke Test

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: Write the integration test**

```python
# tests/test_integration.py
"""Smoke test: create a minimal track using all lib modules and verify MIDI output."""

import os
import pretty_midi
import pytest
from lib.composer import Composer
from lib.constants import BASS_FINGER, GUITAR_OVERDRIVE, GUITAR_DISTORTION, DRUM_CHANNEL
from lib.drums import driving_emo
from lib.harmony import progression, pedal_point
from lib.melody import phrase, spike
from lib.bass import driving_eighths
from lib.humanize import humanize_timing, humanize_velocity, strum
from lib.directives import drone


class TestFullPipeline:
    def test_generate_minimal_track(self, tmp_path):
        c = Composer(99, "test_track", key="Am", tempo=120, time_sig=(4, 4), seed=1)

        # Drums
        drums = c.add_instrument("Drums", program=0, channel=9)
        drum_notes = driving_emo(bars=4, tempo=120, time_sig=(4, 4), seed=1)
        drums.notes.extend(drum_notes)

        # Bass
        bass = c.add_instrument("Bass", program=BASS_FINGER)
        bass_notes = driving_eighths(root=40, bars=4, tempo=120)
        bass_notes = humanize_timing(bass_notes, spread_ms=5, seed=1)
        bass_notes = humanize_velocity(bass_notes, spread=10, seed=1)
        bass.notes.extend(bass_notes)

        # Chords
        chords_inst = c.add_instrument("Chords", program=GUITAR_OVERDRIVE)
        chord_pitches = progression("Am", ["i", "III", "VII", "iv"], bars=4, time_sig=(4, 4))
        beat_dur = c.beat_duration
        for i, pitches in enumerate(chord_pitches):
            bar_start = i * c.bar_duration
            for p in pitches:
                chords_inst.notes.append(pretty_midi.Note(
                    velocity=90, pitch=p, start=bar_start, end=bar_start + c.bar_duration * 0.9,
                ))

        # Melody
        melody_inst = c.add_instrument("Melody", program=GUITAR_DISTORTION)
        mel_notes = phrase("Am", "natural_minor", bars=4, tempo=120, time_sig=(4, 4), seed=1)
        melody_inst.notes.extend(mel_notes)

        # Write MIDI
        out_dir = str(tmp_path)
        path = c.write_midi(output_dir=out_dir)
        assert os.path.exists(path)

        # Verify structure
        loaded = pretty_midi.PrettyMIDI(path)
        assert len(loaded.instruments) == 4
        # All instruments have notes
        for inst in loaded.instruments:
            assert len(inst.notes) > 0

    def test_seed_determinism(self, tmp_path):
        """Same seed produces identical MIDI output."""
        def make_track(seed, out_dir):
            c = Composer(99, "det_test", key="Em", tempo=140, time_sig=(4, 4), seed=seed)
            drums = c.add_instrument("Drums", program=0, channel=9)
            drums.notes.extend(driving_emo(bars=2, tempo=140, seed=seed))
            bass = c.add_instrument("Bass", program=BASS_FINGER)
            bass.notes.extend(driving_eighths(root=40, bars=2, tempo=140))
            return c.write_midi(output_dir=out_dir)

        dir1 = str(tmp_path / "run1")
        dir2 = str(tmp_path / "run2")
        path1 = make_track(42, dir1)
        path2 = make_track(42, dir2)

        midi1 = pretty_midi.PrettyMIDI(path1)
        midi2 = pretty_midi.PrettyMIDI(path2)
        for i1, i2 in zip(midi1.instruments, midi2.instruments):
            assert len(i1.notes) == len(i2.notes)
            for n1, n2 in zip(i1.notes, i2.notes):
                assert n1.pitch == n2.pitch
                assert abs(n1.start - n2.start) < 0.0001
                assert n1.velocity == n2.velocity
```

- [ ] **Step 2: Run the integration test**

Run: `uv run pytest tests/test_integration.py -v`
Expected: all tests PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: integration smoke test for full MIDI generation pipeline"
```

---

### Task 14: Run Full Test Suite & Push

- [ ] **Step 1: Run all tests**

Run: `uv run pytest tests/ -v`
Expected: all tests PASS

- [ ] **Step 2: Push to GitHub**

```bash
git push origin main
```
