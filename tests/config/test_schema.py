"""Tests for configuration schemas."""

import pytest
from pydantic import ValidationError

from words_on_paper.config.schema import (
    BackgroundConfig,
    Effects,
    Font,
    Position,
    ScaleEffect,
    TextSequence,
    VideoConfig,
)


class TestPosition:
    """Test Position configuration."""

    def test_position_default(self) -> None:
        """Test position with defaults."""
        pos = Position()
        assert pos.mode == "center"
        assert pos.x is None
        assert pos.y is None

    def test_position_absolute(self) -> None:
        """Test absolute positioning."""
        pos = Position(mode="absolute", x=100, y=200)
        assert pos.mode == "absolute"
        assert pos.x == 100
        assert pos.y == 200

    def test_position_relative(self) -> None:
        """Test relative positioning."""
        pos = Position(mode="relative", x=0.5, y=0.5)
        assert pos.mode == "relative"
        assert pos.x == 0.5
        assert pos.y == 0.5

    def test_position_negative_coordinates(self) -> None:
        """Test that negative coordinates are rejected."""
        with pytest.raises(ValidationError):
            Position(mode="absolute", x=-10, y=100)


class TestFont:
    """Test Font configuration."""

    def test_font_default(self) -> None:
        """Test font with defaults."""
        font = Font()
        assert font.family == "Arial"
        assert font.size == 72
        assert font.color == "#000000"

    def test_font_custom(self) -> None:
        """Test custom font configuration."""
        font = Font(family="Courier", size=48, color="#FF0000")
        assert font.family == "Courier"
        assert font.size == 48
        assert font.color == "#FF0000"

    def test_font_invalid_size(self) -> None:
        """Test that invalid size is rejected."""
        with pytest.raises(ValidationError):
            Font(size=0)
        with pytest.raises(ValidationError):
            Font(size=-10)


class TestScaleEffect:
    """Test ScaleEffect configuration."""

    def test_scale_effect_default(self) -> None:
        """Test scale effect with defaults."""
        scale = ScaleEffect()
        assert not scale.enabled
        assert scale.initial_scale == 0.5
        assert scale.apply_to_fade_out
        assert scale.easing == "ease_in_out"

    def test_scale_effect_custom(self) -> None:
        """Test scale effect with custom values."""
        scale = ScaleEffect(
            enabled=True,
            initial_scale=0.3,
            apply_to_fade_out=False,
            easing="linear",
        )
        assert scale.enabled
        assert scale.initial_scale == 0.3
        assert not scale.apply_to_fade_out
        assert scale.easing == "linear"

    def test_scale_effect_invalid_scale_too_small(self) -> None:
        """Test that scale < 0 is rejected."""
        with pytest.raises(ValidationError):
            ScaleEffect(initial_scale=0.0)
        with pytest.raises(ValidationError):
            ScaleEffect(initial_scale=-0.1)

    def test_scale_effect_invalid_scale_too_large(self) -> None:
        """Test that scale > 1 is rejected."""
        with pytest.raises(ValidationError):
            ScaleEffect(initial_scale=1.1)

    def test_scale_effect_valid_scale_bounds(self) -> None:
        """Test valid scale boundaries."""
        # Minimum valid value (just above 0)
        scale_min = ScaleEffect(initial_scale=0.0001)
        assert scale_min.initial_scale == pytest.approx(0.0001)

        # Maximum valid value (exactly 1)
        scale_max = ScaleEffect(initial_scale=1.0)
        assert scale_max.initial_scale == 1.0

    def test_scale_effect_invalid_easing(self) -> None:
        """Test that invalid easing is rejected."""
        with pytest.raises(ValidationError):
            ScaleEffect(easing="invalid_easing")

    def test_scale_effect_valid_easing_types(self) -> None:
        """Test all valid easing types."""
        for easing_type in ["linear", "ease_in", "ease_out", "ease_in_out"]:
            scale = ScaleEffect(easing=easing_type)
            assert scale.easing == easing_type


class TestEffects:
    """Test Effects configuration."""

    def test_effects_default(self) -> None:
        """Test effects with defaults."""
        effects = Effects()
        assert not effects.typing.enabled
        assert effects.drop_shadow.enabled
        assert not effects.scale.enabled

    def test_effects_with_scale(self) -> None:
        """Test effects with scale effect enabled."""
        effects = Effects(scale=ScaleEffect(enabled=True, initial_scale=0.6))
        assert effects.scale.enabled
        assert effects.scale.initial_scale == 0.6


class TestTextSequence:
    """Test TextSequence configuration."""

    def test_text_sequence_minimal(self) -> None:
        """Test minimal text sequence."""
        seq = TextSequence(content="Hello World")
        assert seq.content == "Hello World"
        assert seq.start_time == 0.0
        assert seq.fade_in_duration == 1.0
        assert seq.display_duration == 3.0
        assert seq.fade_out_duration == 1.0
        assert seq.orientation == "horizontal"

    def test_text_sequence_full(self) -> None:
        """Test full text sequence configuration."""
        seq = TextSequence(
            content="Test",
            start_time=1.0,
            fade_in_duration=0.5,
            display_duration=2.0,
            fade_out_duration=0.5,
            orientation="vertical",
            position=Position(mode="absolute", x=100, y=200),
            font=Font(size=64),
            z_index=5,
        )
        assert seq.content == "Test"
        assert seq.start_time == 1.0
        assert seq.orientation == "vertical"
        assert seq.position.x == 100
        assert seq.font.size == 64
        assert seq.z_index == 5

    def test_text_sequence_negative_timing(self) -> None:
        """Test that negative timing is rejected."""
        with pytest.raises(ValidationError):
            TextSequence(content="Test", start_time=-1.0)


class TestBackgroundConfig:
    """Test BackgroundConfig."""

    def test_background_default(self) -> None:
        """Test background with defaults."""
        bg = BackgroundConfig()
        assert bg.type == "paper"
        assert bg.color == "#FFFFFF"
        assert bg.texture_intensity == 0.05

    def test_background_invalid_texture(self) -> None:
        """Test invalid texture intensity."""
        with pytest.raises(ValidationError):
            BackgroundConfig(texture_intensity=1.5)
        with pytest.raises(ValidationError):
            BackgroundConfig(texture_intensity=-0.1)


class TestVideoConfig:
    """Test VideoConfig."""

    def test_video_config_default(self) -> None:
        """Test video config with defaults."""
        config = VideoConfig()
        assert config.video["width"] == 1920
        assert config.video["height"] == 1080
        assert config.video["fps"] == 30

    def test_video_config_with_texts(self) -> None:
        """Test video config with text sequences."""
        config = VideoConfig(
            texts=[
                TextSequence(content="First", start_time=0),
                TextSequence(content="Second", start_time=5),
            ]
        )
        assert len(config.texts) == 2
        assert config.texts[0].content == "First"

    def test_video_config_invalid_resolution(self) -> None:
        """Test invalid video resolution."""
        with pytest.raises(ValidationError):
            VideoConfig(video={"width": 0, "height": 1080, "fps": 30})
        with pytest.raises(ValidationError):
            VideoConfig(video={"width": 1920, "height": -100, "fps": 30})

    def test_video_config_invalid_fps(self) -> None:
        """Test invalid fps."""
        with pytest.raises(ValidationError):
            VideoConfig(video={"width": 1920, "height": 1080, "fps": 0})

    def test_get_video_duration_empty(self) -> None:
        """Test duration calculation with no texts."""
        config = VideoConfig()
        assert config.get_video_duration() == 0.0

    def test_get_video_duration_single_text(self) -> None:
        """Test duration calculation with single text."""
        config = VideoConfig(
            texts=[
                TextSequence(
                    content="Test",
                    start_time=0.0,
                    fade_in_duration=1.0,
                    display_duration=3.0,
                    fade_out_duration=1.0,
                )
            ]
        )
        assert config.get_video_duration() == 5.0

    def test_get_video_duration_multiple_texts(self) -> None:
        """Test duration calculation with multiple texts."""
        config = VideoConfig(
            texts=[
                TextSequence(
                    content="First",
                    start_time=0.0,
                    fade_in_duration=1.0,
                    display_duration=2.0,
                    fade_out_duration=1.0,
                ),
                TextSequence(
                    content="Second",
                    start_time=5.0,
                    fade_in_duration=1.0,
                    display_duration=3.0,
                    fade_out_duration=1.0,
                ),
            ]
        )
        assert config.get_video_duration() == 10.0
