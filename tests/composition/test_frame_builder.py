"""Tests for frame building."""

from PIL import Image

from words_on_paper.composition.frame_builder import (
    _calculate_position,
    build_frame,
)
from words_on_paper.config.schema import (
    Position,
    TextSequence,
    VideoConfig,
)


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

    def test_build_frame_with_random_position(self) -> None:
        """Test frame with random positioning mode."""
        config = VideoConfig(
            texts=[
                TextSequence(
                    content="Random",
                    start_time=0,
                    fade_in_duration=0,
                    display_duration=2,
                    fade_out_duration=0,
                    position=Position(mode="random"),
                )
            ]
        )
        frame = build_frame(config, 0.5)
        assert isinstance(frame, Image.Image)

    def test_calculate_position_random_mode(self) -> None:
        """Test position calculation with random mode."""
        position_config = Position(mode="random")
        text_width = 100
        text_height = 50
        video_width = 1920
        video_height = 1080

        # Calculate position for specific text
        x1, y1 = _calculate_position(
            position_config, text_width, text_height, video_width, video_height, "test"
        )

        # Same text should produce same position (deterministic)
        x2, y2 = _calculate_position(
            position_config, text_width, text_height, video_width, video_height, "test"
        )
        assert x1 == x2
        assert y1 == y2

        # Different text should produce different position
        x3, y3 = _calculate_position(
            position_config, text_width, text_height, video_width, video_height, "other"
        )
        assert not (x1 == x3 and y1 == y3)

        # Position should be within 20-80% bounds
        assert x1 >= int(video_width * 0.2)
        assert x1 <= int(video_width * 0.8 - text_width)
        assert y1 >= int(video_height * 0.2)
        assert y1 <= int(video_height * 0.8 - text_height)

    def test_build_frame_with_scale_effect(self) -> None:
        """Test frame building with scale effect enabled."""
        config = VideoConfig(
            texts=[
                TextSequence(
                    content="Scaled",
                    start_time=0,
                    fade_in_duration=1,
                    display_duration=2,
                    fade_out_duration=1,
                    effects={"scale": {"enabled": True, "initial_scale": 0.5}},
                )
            ]
        )
        # During fade-in, text should be scaled
        frame_fade_in = build_frame(config, 0.5)
        assert isinstance(frame_fade_in, Image.Image)

        # During display, text should be at full scale
        frame_display = build_frame(config, 1.5)
        assert isinstance(frame_display, Image.Image)

        # During fade-out, text should be scaled
        frame_fade_out = build_frame(config, 3.5)
        assert isinstance(frame_fade_out, Image.Image)

    def test_build_frame_scale_effect_fade_out_disabled(self) -> None:
        """Test scale effect with fade-out effect disabled."""
        config = VideoConfig(
            texts=[
                TextSequence(
                    content="No Fade Out Scale",
                    start_time=0,
                    fade_in_duration=1,
                    display_duration=2,
                    fade_out_duration=1,
                    effects={
                        "scale": {
                            "enabled": True,
                            "initial_scale": 0.5,
                            "apply_to_fade_out": False,
                        }
                    },
                )
            ]
        )
        frame = build_frame(config, 3.5)  # During fade-out
        assert isinstance(frame, Image.Image)

    def test_build_frame_scale_effect_different_easing(self) -> None:
        """Test scale effect with different easing types."""
        for easing in ["linear", "ease_in", "ease_out", "ease_in_out"]:
            config = VideoConfig(
                texts=[
                    TextSequence(
                        content="Easing Test",
                        start_time=0,
                        fade_in_duration=1,
                        display_duration=2,
                        fade_out_duration=1,
                        effects={
                            "scale": {
                                "enabled": True,
                                "initial_scale": 0.5,
                                "easing": easing,
                            }
                        },
                    )
                ]
            )
            frame = build_frame(config, 0.5)  # During fade-in
            assert isinstance(frame, Image.Image)

    def test_build_frame_scale_with_typing_effect(self) -> None:
        """Test scale effect combined with typing effect."""
        config = VideoConfig(
            texts=[
                TextSequence(
                    content="Scaled Typing",
                    start_time=0,
                    fade_in_duration=0.5,
                    display_duration=2,
                    fade_out_duration=0.5,
                    effects={
                        "scale": {"enabled": True, "initial_scale": 0.5},
                        "typing": {"enabled": True, "chars_per_second": 2},
                        "drop_shadow": {"enabled": False},
                    },
                )
            ]
        )
        frame = build_frame(config, 1.0)
        assert isinstance(frame, Image.Image)
