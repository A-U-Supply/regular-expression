# Regular Expression

A 34-track experimental emo MIDI album. Every track is exactly 30 seconds long.

Short, aggressive, emotionally dense sketches — hardcore punk brevity meets emo harmony meets experimental structure. Generated programmatically in Python using `pretty_midi`, rendered to audio via `fluidsynth`.

## The Album

| #  | Title              | #  | Title              |
|----|--------------------|----|--------------------|
| 01 | wtf                | 18 | what the hell      |
| 02 | wth                | 19 | fuck broken        |
| 03 | ffs                | 20 | fuck useless       |
| 04 | omfg               | 21 | fuck terrible      |
| 05 | shit               | 22 | fuck awful         |
| 06 | shitty             | 23 | fuck horrible      |
| 07 | shittiest          | 24 | fucking broken     |
| 08 | dumbass            | 25 | fucking useless    |
| 09 | horrible           | 26 | fucking terrible   |
| 10 | awful              | 27 | fucking awful      |
| 11 | piss off           | 28 | fucking horrible   |
| 12 | pissed off         | 29 | fuck you           |
| 13 | pissing off        | 30 | screw this         |
| 14 | piece of shit      | 31 | screw you          |
| 15 | piece of crap      | 32 | so frustrating     |
| 16 | piece of junk      | 33 | this sucks         |
| 17 | what the fuck      | 34 | damn it            |

## Setup

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) for Python package management
- [fluidsynth](https://www.fluidsynth.org/) for MIDI-to-audio rendering

### Install

```bash
# Install fluidsynth (macOS)
brew install fluidsynth

# Install Python dependencies
uv sync

# Download the GM soundfont (~140MB)
./setup.sh
```

## Usage

### Generate a single track

```bash
# Generate the "album version" (deterministic default seed)
uv run python tracks/01_wtf.py

# Generate a variation with a different seed
uv run python tracks/01_wtf.py --seed 42

# Skip audio rendering (MIDI only, faster)
uv run python tracks/01_wtf.py --no-render
```

### Generate the full album

```bash
# Generate all 34 tracks (MIDI + WAV)
uv run python scripts/render_all.py

# Assemble into one continuous album file
uv run python scripts/assemble_album.py
```

### Output

- `midi_output/` — MIDI files (`01_wtf.mid`, `02_wth.mid`, ...)
- `wav_output/` — WAV files (`01_wtf.wav`, `02_wth.wav`, ...)
- `wav_output/regular_expression.wav` — the full album as one file

## Architecture

### Shared library (`lib/`)

Low-level music theory primitives and a thin plumbing layer:

| Module | Purpose |
|--------|---------|
| `constants.py` | GM mappings, scales, key palette, velocity ranges |
| `humanize.py` | Seed-controlled timing offsets, velocity variation, strum simulation, ghost notes |
| `harmony.py` | Chord voicings, progressions, clusters, chromatic mediants, pedal points |
| `melody.py` | Contour builders, phrase generators, spikes, stutters, broken trails |
| `bass.py` | Kick-locked bass, driving eighths, counter-melodies, chromatic approaches |
| `drums.py` | Pattern builders (driving emo, blast, half-time, floor tom, no-snare), fills |
| `directives.py` | Structural techniques (The Collapse, Loop That Breaks, Two Songs Stitched, etc.) |
| `composer.py` | `Composer` class — creates PrettyMIDI objects, manages instruments, writes output |
| `render.py` | Fluidsynth wrapper for MIDI-to-WAV rendering |

### Per-track scripts (`tracks/`)

Each track is a standalone Python script that imports from `lib/` and composes a 30-second piece. Track scripts are where the creative decisions live — key, tempo, time signature, instrument choices, structure, which directives to apply.

### Seed system

Every track has a default seed (derived from its track number) that produces a deterministic "album version." Pass `--seed N` for variations — different but always within the emo theory rules.

## Music Theory

- **Keys**: Am, Em, Bm, Dm, F#m. Phrygian for aggression, Dorian for melancholy. Major keys banned unless ironic.
- **Tempo**: 90–160 BPM, varied across the album.
- **Time signatures**: ~60% in 4/4, ~20% waltz (3/4, 6/8), ~20% odd meter (5/4, 7/8, mixed).
- **Harmony**: Open voicings, chromatic mediants, clusters, pedal points. No closed triads.
- **Melody**: Mostly descending. Asymmetric phrases. Gaps for breathing. High-note-to-drop is the money move.
- **Bass**: Locks with kick 60% of the time, drifts the other 40%. Ghost notes for physical feel.
- **Drums**: Humanized timing (never quantized). Driving emo, blast beats, half-time, floor tom pulse. Ghost snares. Crashes only at section boundaries.

## Special Directives

Structural techniques applied 1–2 per track, distributed across the album:

1. **The Collapse** — everything drops to one fragile instrument, then re-enters louder
2. **The Loop That Breaks** — a repeating passage that mutates until unrecognizable
3. **Two Songs Stitched** — two ideas in different tempo/key connected by noise
4. **The Countdown** — sections get progressively shorter (8→4→2→1 bars)
5. **Unison Collapse** — all instruments converge on one note, then explode outward
6. **Reverse Structure** — starts at climax, strips away to silence
7. **Rhythmic Displacement** — one instrument shifted by an 8th note from the grid
8. **The Drone** — one low note sustains underneath everything for the full 30 seconds

## Album Arc

The 34 tracks follow a deliberate emotional trajectory:

- **01–04** (wtf → omfg): Escalating confusion. Disoriented to unhinged.
- **05–07** (shit → shittiest): A descent. Each heavier and slower. Sinking trilogy.
- **08–10** (dumbass → awful): Contempt turning inward. Ugly and angular.
- **11–13** (piss off → pissing off): Tense conjugation trilogy. Same material mutated three ways.
- **14–16** (piece of shit → piece of junk): Degradation. Aggressive to defeated to hollowed out.
- **17–18** (what the fuck / what the hell): Twin tracks. Same melody, different harmonization.
- **19–28** (fuck/fucking series): The brutal center. 10 tracks of relentless variation on anger.
- **29–31** (fuck you → screw you): Confrontational. The most "song-like" structures.
- **32–34** (so frustrating → damn it): Deflation. The last track ends mid-phrase, unresolved.

## License

TBD
