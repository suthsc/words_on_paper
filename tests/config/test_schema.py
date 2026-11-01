"""Tests for configuration schemas."""

import pytest
from pydantic import ValidationError

from words_on_paper.config.schema import (
    BackgroundConfig,
    Effects,
    Font,
    LetterSpacingEffect,
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


class TestLetterSpacingEffect:
    """Test LetterSpacingEffect configuration."""

    def test_letter_spacing_effect_default(self) -> None:
        """Test letter spacing effect with defaults."""
        effect = LetterSpacingEffect()
        assert not effect.enabled
        assert effect.initial_spacing == 1.0
        assert effect.target_spacing == 0.7
        assert effect.apply_to_fade_out
        assert effect.easing == "ease_in_out"

    def test_letter_spacing_effect_custom(self) -> None:
        """Test letter spacing effect with custom values."""
        effect = LetterSpacingEffect(
            enabled=True,
            initial_spacing=1.2,
            target_spacing=0.8,
            apply_to_fade_out=False,
            easing="linear",
        )
        assert effect.enabled
        assert effect.initial_spacing == 1.2
        assert effect.target_spacing == 0.8
        assert not effect.apply_to_fade_out
        assert effect.easing == "linear"

    def test_letter_spacing_effect_invalid_initial_spacing_zero(self) -> None:
        """Test that initial_spacing <= 0 is rejected."""
        with pytest.raises(ValidationError):
            LetterSpacingEffect(initial_spacing=0.0)
        with pytest.raises(ValidationError):
            LetterSpacingEffect(initial_spacing=-0.5)

    def test_letter_spacing_effect_invalid_target_spacing_zero(self) -> None:
        """Test that target_spacing <= 0 is rejected."""
        with pytest.raises(ValidationError):
            LetterSpacingEffect(target_spacing=0.0)
        with pytest.raises(ValidationError):
            LetterSpacingEffect(target_spacing=-0.5)

    def test_letter_spacing_effect_valid_spacing_bounds(self) -> None:
        """Test valid spacing boundaries."""
        # Very small valid values
        effect_small = LetterSpacingEffect(initial_spacing=0.01, target_spacing=0.01)
        assert effect_small.initial_spacing == pytest.approx(0.01)

        # Large valid values
        effect_large = LetterSpacingEffect(initial_spacing=5.0, target_spacing=5.0)
        assert effect_large.initial_spacing == 5.0

    def test_letter_spacing_effect_invalid_easing(self) -> None:
        """Test that invalid easing is rejected."""
        with pytest.raises(ValidationError):
            LetterSpacingEffect(easing="invalid_easing")

    def test_letter_spacing_effect_valid_easing_types(self) -> None:
        """Test all valid easing types."""
        for easing_type in ["linear", "ease_in", "ease_out", "ease_in_out"]:
            effect = LetterSpacingEffect(easing=easing_type)
            assert effect.easing == easing_type

    def test_letter_spacing_effect_center_spacing_default(self) -> None:
        """Test center_spacing defaults to False."""
        effect = LetterSpacingEffect()
        assert not effect.center_spacing

    def test_letter_spacing_effect_center_spacing_enabled(self) -> None:
        """Test center_spacing can be enabled."""
        effect = LetterSpacingEffect(center_spacing=True)
        assert effect.center_spacing

    def test_letter_spacing_effect_center_spacing_with_other_params(self) -> None:
        """Test center_spacing combined with other parameters."""
        effect = LetterSpacingEffect(
            enabled=True,
            initial_spacing=1.2,
            target_spacing=0.6,
            center_spacing=True,
            easing="ease_in_out",
        )
        assert effect.enabled
        assert effect.center_spacing
        assert effect.initial_spacing == 1.2
        assert effect.target_spacing == 0.6


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


class TestCascadingStyles:
    """Test defaults/styles integration in VideoConfig."""

    def test_defaults_only(self) -> None:
        """defaults apply to every text; schema defaults fill the rest."""
        config = VideoConfig(
            defaults={"font": {"family": "Courier", "size": 40}, "z_index": 3},
            texts=[{"content": "a"}, {"content": "b", "font": {"size": 10}}],
        )
        assert config.texts[0].font.family == "Courier"
        assert config.texts[0].font.size == 40
        assert config.texts[0].font.color == "#000000"
        assert config.texts[0].z_index == 3
        assert config.texts[1].font.family == "Courier"
        assert config.texts[1].font.size == 10

    def test_style_only(self) -> None:
        """A referenced style is applied and recorded on the text."""
        config = VideoConfig(
            styles={"vlad": {"font": {"color": "#1A5490"}, "position": {"x": 0.15}}},
            texts=[{"content": "a", "style": "vlad"}],
        )
        text = config.texts[0]
        assert text.font.color == "#1A5490"
        assert text.position.x == 0.15
        assert text.style == "vlad"

    def test_inline_overrides_style_and_defaults(self) -> None:
        """Inline fields beat styles, which beat defaults."""
        config = VideoConfig(
            defaults={"fade_in_duration": 0.1, "z_index": 1},
            styles={"s": {"fade_in_duration": 0.2, "z_index": 2}},
            texts=[{"content": "a", "style": "s", "z_index": 9}],
        )
        assert config.texts[0].fade_in_duration == 0.2
        assert config.texts[0].z_index == 9

    def test_unknown_field_in_style(self) -> None:
        """A typo inside a style fails loudly with its path."""
        with pytest.raises(ValidationError, match=r"styles\.vlad\.font\.colour"):
            VideoConfig(styles={"vlad": {"font": {"colour": "#FFFFFF"}}}, texts=[])

    def test_unknown_field_in_defaults(self) -> None:
        """A typo inside defaults fails loudly with its path."""
        with pytest.raises(ValidationError, match=r"defaults\.effects\.typng"):
            VideoConfig(defaults={"effects": {"typng": {"enabled": True}}})

    def test_style_key_forbidden_in_defaults_and_styles(self) -> None:
        """'style' is only meaningful on texts; styles use 'extends'."""
        with pytest.raises(ValidationError, match=r"defaults\.style: not allowed"):
            VideoConfig(defaults={"style": "x"})
        with pytest.raises(ValidationError, match=r"styles\.a\.style: not allowed"):
            VideoConfig(styles={"a": {"style": "b"}, "b": {}})

    def test_extends_only_in_styles(self) -> None:
        """'extends' is accepted in styles but is an unknown field in defaults."""
        VideoConfig(styles={"a": {"z_index": 1}, "b": {"extends": "a"}})
        with pytest.raises(ValidationError, match=r"defaults\.extends: unknown"):
            VideoConfig(defaults={"extends": "a"}, styles={"a": {}})

    def test_unknown_style_ref(self) -> None:
        """Referencing a missing style names the text."""
        with pytest.raises(ValidationError, match=r"texts\[0\]: unknown style 'nope'"):
            VideoConfig(texts=[{"content": "a", "style": "nope"}])

    def test_style_cycle(self) -> None:
        """A cycle in extends is reported."""
        with pytest.raises(ValidationError, match="a -> b -> a"):
            VideoConfig(
                styles={"a": {"extends": "b"}, "b": {"extends": "a"}},
                texts=[{"content": "x", "style": "a"}],
            )

    def test_bad_value_from_style_names_text_and_style(self) -> None:
        """An invalid value coming from a style mentions the text and style."""
        with pytest.raises(
            ValidationError, match=r"texts\[0\] \(style: big\): font\.size"
        ):
            VideoConfig(
                styles={"big": {"font": {"size": -5}}},
                texts=[{"content": "a", "style": "big"}],
            )

    def test_style_may_set_content(self) -> None:
        """Styles may set any field, including content."""
        config = VideoConfig(
            styles={"pause": {"content": "(Pause.)"}}, texts=[{"style": "pause"}]
        )
        assert config.texts[0].content == "(Pause.)"

    def test_duration_from_defaults(self) -> None:
        """get_video_duration uses timings that come only from defaults."""
        config = VideoConfig(
            defaults={
                "fade_in_duration": 0.5,
                "display_duration": 1.0,
                "fade_out_duration": 0.5,
            },
            styles={"late": {"start_time": 10.0}},
            texts=[{"content": "a"}, {"content": "b", "style": "late"}],
        )
        assert config.get_video_duration() == 12.0

    def test_no_styles_unchanged(self) -> None:
        """Configs without defaults/styles behave exactly as before."""
        config = VideoConfig(texts=[{"content": "a"}])
        assert config.defaults == {}
        assert config.styles == {}
        assert config.texts[0].style is None
        assert config.texts[0].font == Font()
