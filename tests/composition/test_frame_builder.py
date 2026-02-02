"""Tests for frame building."""

from PIL import Image

from words_on_paper.composition.frame_builder import build_frame
from words_on_paper.config.schema import TextSequence, VideoConfig


class TestBuildFrame:
    """Test frame building."""

    def test_build_frame_empty_config(self) -> None:
        """Test building frame with empty config."""
        config = VideoConfig()
        frame = build_frame(config, 0.0)
        assert isinstance(frame, Image.Image)
        assert frame.size == (1920, 1080)
        assert frame.mode == "RGB"

    def test_build_frame_with_text(self) -> None:
        """Test building frame with text."""
        config = VideoConfig(
            texts=[
                TextSequence(
                    content="Hello",
                    start_time=0,
                    fade_in_duration=0,
                    display_duration=5,
                    fade_out_duration=0,
                )
            ]
        )
        frame = build_frame(config, 0.5)
        assert isinstance(frame, Image.Image)
        assert frame.mode == "RGB"

    def test_build_frame_before_text(self) -> None:
        """Test frame before text appears."""
        config = VideoConfig(
            texts=[
                TextSequence(
                    content="Hello",
                    start_time=2,
                    fade_in_duration=1,
                    display_duration=2,
                    fade_out_duration=1,
                )
            ]
        )
        frame = build_frame(config, 0.0)
        assert isinstance(frame, Image.Image)

    def test_build_frame_during_text(self) -> None:
        """Test frame during text display."""
        config = VideoConfig(
            texts=[
                TextSequence(
                    content="Hello",
                    start_time=0,
                    fade_in_duration=1,
                    display_duration=2,
                    fade_out_duration=1,
                )
            ]
        )
        frame = build_frame(config, 1.5)
        assert isinstance(frame, Image.Image)

    def test_build_frame_after_text(self) -> None:
        """Test frame after text disappears."""
        config = VideoConfig(
            texts=[
                TextSequence(
                    content="Hello",
                    start_time=0,
                    fade_in_duration=1,
                    display_duration=2,
                    fade_out_duration=1,
                )
            ]
        )
        frame = build_frame(config, 10.0)
        assert isinstance(frame, Image.Image)

    def test_build_frame_multiple_texts(self) -> None:
        """Test frame with multiple texts."""
        config = VideoConfig(
            texts=[
                TextSequence(
                    content="First",
                    start_time=0,
                    fade_in_duration=0.5,
                    display_duration=2,
                    fade_out_duration=0.5,
                ),
                TextSequence(
                    content="Second",
                    start_time=3,
                    fade_in_duration=0.5,
                    display_duration=2,
                    fade_out_duration=0.5,
                ),
            ]
        )
        frame = build_frame(config, 1.0)
        assert isinstance(frame, Image.Image)

    def test_build_frame_with_typing_effect(self) -> None:
        """Test frame with typing effect enabled."""
        config = VideoConfig(
            texts=[
                TextSequence(
                    content="Hello World",
                    start_time=0,
                    fade_in_duration=0,
                    display_duration=5,
                    fade_out_duration=0,
                    effects={
                        "typing": {
                            "enabled": True,
                            "chars_per_second": 2,
                        },
                        "drop_shadow": {"enabled": False},
                    },
                )
            ]
        )
        frame = build_frame(config, 0.5)
        assert isinstance(frame, Image.Image)

    def test_build_frame_custom_resolution(self) -> None:
        """Test frame with custom video resolution."""
        config = VideoConfig(
            video={"width": 1280, "height": 720, "fps": 24},
            texts=[
                TextSequence(
                    content="Test",
                    start_time=0,
                    fade_in_duration=0,
                    display_duration=2,
                    fade_out_duration=0,
                )
            ],
        )
        frame = build_frame(config, 0.5)
        assert frame.size == (1280, 720)
