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
