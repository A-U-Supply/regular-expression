# Regular Expression — Experimental Emo MIDI Album Design

## Overview

**Regular Expression** is a 34-track experimental emo MIDI album. Every track is exactly 30 seconds long — short, aggressive, emotionally dense sketches. Hardcore punk brevity meets emo harmony meets experimental structure.

The project is a Python codebase that generates MIDI files programmatically using `pretty_midi`, then renders them to WAV using `fluidsynth` with a GM soundfont. Each track is its own script. A shared library provides music theory primitives and plumbing so track scripts stay focused on composition.

## Repo Structure

```
regular-expression/
├── README.md
├── pyproject.toml              # uv project — deps: pretty_midi, numpy, soundfile
├── setup.sh                    # downloads FluidR3_GM.sf2 soundfont
├── soundfonts/                 # .gitignored, populated by setup.sh
│   └── FluidR3_GM.sf2
├── lib/                        # shared primitives + composer
│   ├── __init__.py
│   ├── composer.py             # Composer class — MIDI/file plumbing
│   ├── drums.py                # drum pattern builders
│   ├── harmony.py              # chord voicings, progressions, clusters
│   ├── melody.py               # melody contour builders, broken melodies
│   ├── bass.py                 # bass line builders, ghost notes
│   ├── humanize.py             # timing offsets, velocity variation, seed control
│   ├── constants.py            # GM mappings, scale definitions, tempo/vel ranges
│   ├── directives.py           # special structural directives
│   └── render.py               # fluidsynth .mid -> .wav rendering
├── tracks/                     # one script per track
│   ├── 01_wtf.py
│   ├── 02_wth.py
│   ├── ...
│   └── 34_damn_it.py
├── midi_output/                # generated .mid files
├── wav_output/                 # rendered .wav files
├── scripts/
│   ├── render_all.py           # run all track scripts, render wavs
│   └── assemble_album.py       # concatenate wavs into full album
└── docs/
```

## Shared Library (`lib/`)

### `constants.py`

GM instrument mappings:
- **Bass**: Program 33 (Electric Bass Finger), 34 (Electric Bass Pick)
- **Melody**: Program 29 (Overdriven Guitar), 30 (Distortion Guitar), 81 (Lead 1 Square)
- **Chords**: Program 27 (Electric Guitar Clean), 29 (Overdriven Guitar), 89 (Pad 2 Warm)
- **Drums**: Channel 10 (GM percussion)

GM drum map:
| Note | Sound         |
|------|---------------|
| 36   | Kick          |
| 37   | Rim Click     |
| 38   | Snare         |
| 42   | Closed Hi-Hat |
| 43   | Floor Tom     |
| 46   | Open Hi-Hat   |
| 47   | Rack Tom      |
| 49   | Crash         |
| 51   | Ride          |

Scale definitions: natural minor, Phrygian, Dorian, chromatic.

Emo key palette: Am, Em, Bm, Dm, F#m.

Velocity ranges:
- Whisper: 20-40
- Quiet: 40-60
- Normal: 70-100
- Loud: 100-120
- Max: 120-127

Track duration: 30.0 seconds.

### `humanize.py`

Seed-controlled RNG. Every function takes an optional `seed` parameter. Default seed per track (derived from track number) produces the "album version." Different seed = recognizable variation within genre constraints.

Functions:
- `humanize_timing(notes, spread_ms=10)` — offset note starts by +/-spread_ms
- `humanize_velocity(notes, spread=15)` — vary velocity within genre-valid bounds
- `strum(chord_notes, direction="down", spread_ms=20)` — stagger chord tones to simulate strumming, lowest note first for down-strums
- `ghost_notes(notes, probability=0.3, vel_range=(15, 40))` — insert low-velocity ghost hits between main notes

### `harmony.py`

- `chord(root, quality, octave, voicing="open")` — returns list of MIDI pitches. Open voicings spread across octaves 2-5. Qualities: min, min7, maj7, sus2, sus4, add9, dim, aug, power
- `progression(key, numerals, bars, time_sig)` — generates chord sequence from Roman numerals (e.g., `["i", "III", "VII", "iv"]`)
- `cluster(center_pitch, width=2)` — adjacent semitones for harmonic crush moments
- `chromatic_mediant(chord, direction)` — jump a major/minor 3rd for emotional shifts
- `pedal_point(pitch, duration)` — sustained note under moving chords

### `melody.py`

- `contour(key, mode, direction="descending", range_interval=5)` — generate a melodic shape within constraints
- `phrase(key, mode, bars, time_sig, density)` — asymmetric phrases (3-bar, 5-bar) with gaps
- `spike(base_pitch, interval="min7")` — leap up then immediate drop
- `stutter(pitch, count, rhythm)` — obsessive single-note repetition
- `broken_trail(phrase, decay_point)` — phrase that trails into nothing

### `bass.py`

- `locked_bass(kick_pattern, root, fifth)` — bass that follows kick ~60% of time, drifts 40%
- `driving_eighths(root, bars)` — repeated 8ths on one note, wall of sound
- `counter_melody(key, mode, bars)` — wide-interval bass melody (min7, octave, tritone)
- `chromatic_approach(target, direction, length)` — half-step slide into root
- Ghost notes handled via `humanize.ghost_notes()`

### `drums.py`

- `driving_emo(bars, time_sig)` — kick 1+3, snare 2+4, 8th hats
- `blast(bars)` — kick+snare alternating 16ths (capped at 4 bars)
- `half_time(bars, time_sig)` — snare on beat 3 only
- `floor_tom_pulse(bars, time_sig)` — floor tom replaces kick
- `no_snare(bars, time_sig)` — kick, hat, toms only
- `fill(beats=1, instruments=["tom", "snare"])` — short stumbling fills
- All patterns return note lists with humanized timing built in

### `directives.py`

Eight special structural directives, each used at least twice across the album, 1-2 per track:

1. **The Collapse** — `collapse(composer, solo_instrument, re_entry_bar, vel_boost=20)` — mutes all except one instrument playing something fragile, then all re-enter louder
2. **The Loop That Breaks** — `loop_that_breaks(notes, repetitions=4, mutations=["drop_notes", "shift_beats", "wrong_pitch"])` — repeats a passage with cumulative mutations
3. **Two Songs Stitched** — `two_songs_stitched(composer, song_a_bars, song_b_bars, transition_bars=1)` — returns bar boundaries for two different ideas with cluster/noise transition
4. **The Countdown** — `countdown(section_bars=[8, 4, 2, 1])` — returns bar boundaries for progressively shorter sections
5. **Unison Collapse** — `unison_collapse(instruments, target_pitch, sustain_bars=2)` — converges all instruments to one note, then returns
6. **Reverse Structure** — `reverse_structure(composer)` — returns bar plan starting at climax, stripping instruments one by one
7. **Rhythmic Displacement** — `rhythmic_displacement(notes, offset_eighths=1)` — shifts one instrument's notes by an 8th note
8. **The Drone** — `drone(composer, pitch, instrument_program=33)` — sustained low note for the full 30 seconds

### `render.py`

- `render_wav(mid_path, wav_path, soundfont_path)` — calls fluidsynth to render MIDI to WAV

### `composer.py`

- `Composer(track_number, title, key, tempo, time_sig, seed=None)` — plumbing class that handles:
  - Creating the `PrettyMIDI` object with tempo
  - `add_instrument(name, program, channel)` — returns the instrument for direct note manipulation
  - `write_midi()` — saves to `midi_output/NN_title.mid`
  - `render()` — calls render.py to produce `wav_output/NN_title.wav`
  - `duration` property — always 30.0 seconds
  - Seed management — flows seed into humanize functions

## Per-Track Scripts

Each track script in `tracks/` follows this pattern:

```python
from lib.composer import Composer
from lib.drums import driving_emo
from lib.harmony import progression
from lib.humanize import humanize_timing, humanize_velocity

def generate(seed=None):
    c = Composer(1, "wtf", key="Am", tempo=130, time_sig=(4, 4), seed=seed)

    drums = c.add_instrument("Drums", program=0, channel=10)
    bass = c.add_instrument("Bass", program=33)
    chords = c.add_instrument("Chords", program=29)
    melody = c.add_instrument("Melody", program=30)

    # ... composition using lib primitives ...

    c.write_midi()
    c.render()

if __name__ == "__main__":
    generate()
```

### CLI interface

Each script accepts via argparse:
- `--seed 42` — override seed for variation
- `--no-render` — skip wav rendering for faster iteration

### Seed system

- `seed=None` -> default seed (derived from track number) -> deterministic "album version"
- Any other integer seed -> different but genre-valid variation
- Seed flows through Composer into all `humanize_*` calls and randomized primitives (note selection from scale, ghost note placement, velocity curves)
- Same seed always produces same output

## Trilogy & Twin Track Consistency

Some track groups share musical material:

- **Tracks 5-7** (shit/shitty/shittiest): Share a common motif that degrades. Each heavier and slower.
- **Tracks 11-13** (piss off/pissed off/pissing off): Same core material mutated via tempo shift, key shift, structural inversion. First track defines shared material.
- **Tracks 14-16** (piece of shit/crap/junk): Degradation trilogy. Start aggressive, end defeated.
- **Tracks 17-18** (what the fuck/what the hell): Twin tracks. Same melody, different harmonization. One furious, one exhausted.

For these, the first track in the group defines shared material, and subsequent scripts import/reference it.

## Scripts

### `scripts/render_all.py`
Runs all 34 track scripts in sequence, then renders WAVs.

### `scripts/assemble_album.py`
Concatenates all WAVs in track order into `wav_output/regular_expression.wav`.

## Music Theory Rules

### Key & Mode
- Default palette: Am, Em, Bm, Dm, F#m
- Phrygian for most aggressive tracks (b2 = dread)
- Dorian for melancholy-but-not-crushed
- Major keys banned unless used ironically (bright passage that collapses into dissonance)

### Tempo
- Range: 90-160 BPM
- At 30s: 90 BPM ~ 12 bars, 160 BPM ~ 21 bars
- Varied across the album

### Time Signatures
- ~60% in 4/4
- ~20% in 3/4 or 6/8
- ~20% in odd meter: 5/4, 7/8, or mixed

### Harmony
- Core progressions: i-III-VII-iv, i-VI-III-VII, i-iv-v-i, vi-IV-I-V
- Open voicings: root in octave 2-3, upper tones in octave 4-5
- Chord types: min, min7, maj7, sus2, sus4, add9, dim, aug, power chords
- Chromatic mediants for emotional shifts
- Staggered attacks (10-30ms offset) for strum simulation
- Clusters on 8-10 tracks (adjacent semitones)
- Pedal points (sustained 5th or tritone under moving chords)

### Melody
- Range: C3-B5, most phrases within a 5th
- Mostly descending contour. Rising = desperate. High note -> drop = money move.
- Intervals: min 2nds, min 3rds, P4ths, tritones, P5ths for clarity
- Asymmetric phrasing (3-bar, 5-bar). Gaps between phrases.
- Velocity 40-120, highly varied with swells and unexpected accents
- Some tracks: obsessive repetition, stutters, trailing phrases

### Bass
- Range: C1-D4, mostly octaves 1-3
- Lock with kick ~60%, drift 40%
- Root-5th movement, octave drops, chromatic approaches
- Heavy sections: repeated 8ths/16ths
- Counter-melody on 8-10 tracks (wide intervals)
- Ghost notes (vel 20-40) between main hits

### Drums
- Pattern variety: driving emo, blast/breakdown, half-time, floor tom pulse, no-snare
- Hi-hat velocity constantly fluctuating 50-110, open hat on upbeats
- Occasional snare on "and" of 2 or 4
- Ghost snares at vel 15-35
- Crashes only at section boundaries
- Short fills (1-2 beats), stumbling
- Humanized timing: +/-5-15ms from grid

### Dynamics & Texture
- Wide velocity range. Quiet (30-60) vs. loud (100-127).
- Aggressive use of rests. Sudden gaps.
- At least 5 tracks with a moment where all instruments drop to one.

## Album Arc

| Group | Tracks | Arc | Character |
|-------|--------|-----|-----------|
| Escalating confusion | 01-04 | Disoriented -> unhinged | Mid-tempo to fast |
| A descent | 05-07 | Each heavier and slower | Sinking trilogy |
| Contempt inward | 08-10 | Ugly, angular, self-lacerating | |
| Tense conjugation | 11-13 | Same material mutated 3 ways | Tempo/key/structure shifts |
| Degradation | 14-16 | Aggressive -> defeated -> hollowed | |
| Twin tracks | 17-18 | Same melody, different harmonization | Furious vs. exhausted |
| Brutal center | 19-28 | Relentless anger variation | Most experimental, wildly varied |
| Confrontation | 29-31 | Directed outward | Most "song-like" structures |
| Deflation | 32-34 | Energy draining | Last track ends mid-phrase, unresolved |

## Directive Distribution (Planned)

| Directive | Target Track Groups |
|-----------|-------------------|
| The Collapse | 3-4 tracks across album |
| Loop That Breaks | 3-4 tracks, clustered in experimental center (19-28) |
| Two Songs Stitched | 2-3 tracks |
| The Countdown | 2-3 tracks |
| Unison Collapse | 2-3 tracks |
| Reverse Structure | 2-3 tracks, including track 34 |
| Rhythmic Displacement | 3-4 tracks |
| The Drone | 3-4 tracks |

## Setup & Dependencies

### Python dependencies (via uv)
- `pretty_midi` — MIDI generation
- `numpy` — numeric operations for humanization
- `soundfile` — WAV file handling for album assembly

### External dependencies
- `fluidsynth` — installed via Homebrew (`brew install fluidsynth`)
- `FluidR3_GM.sf2` — downloaded by `setup.sh` into `soundfonts/`

### Setup flow
1. `uv sync` — install Python deps
2. `brew install fluidsynth` (if not present)
3. `./setup.sh` — download soundfont

## Composition Workflow

For each track (or batch of 3-5):
1. Pitch concept: emotional interpretation, key, tempo, time sig, instruments, directives, structural sketch, theory moves
2. User approves or adjusts
3. Write the track script using lib primitives
4. Run it — generate MIDI + WAV
5. User listens, gives feedback, we tweak if needed
6. Move on
