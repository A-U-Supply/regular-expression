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
