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
