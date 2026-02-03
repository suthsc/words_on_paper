"""Tests for animation calculations."""

import pytest

from words_on_paper.composition.animator import (
    calculate_scale_factor,
    calculate_text_opacity,
    calculate_visible_chars,
)


class TestCalculateTextOpacity:
    """Test text opacity calculation."""

    def test_opacity_before_start(self) -> None:
        """Test opacity is 0 before start time."""
        opacity = calculate_text_opacity(0, 1, 1, 2, 1)
        assert opacity == 0.0

    def test_opacity_fade_in_start(self) -> None:
        """Test opacity at fade in start."""
        opacity = calculate_text_opacity(1, 1, 1, 2, 1)
        assert opacity == 0.0

    def test_opacity_fade_in_middle(self) -> None:
        """Test opacity at fade in middle."""
        opacity = calculate_text_opacity(1.5, 1, 1, 2, 1)
        assert 0.0 < opacity < 1.0

    def test_opacity_fade_in_end(self) -> None:
        """Test opacity at fade in end."""
        opacity = calculate_text_opacity(2, 1, 1, 2, 1)
        assert opacity == 1.0

    def test_opacity_display_phase(self) -> None:
        """Test opacity during display phase."""
        opacity = calculate_text_opacity(2.5, 1, 1, 2, 1)
        assert opacity == 1.0

    def test_opacity_display_end(self) -> None:
        """Test opacity at display end."""
        opacity = calculate_text_opacity(4, 1, 1, 2, 1)
        assert opacity == 1.0

    def test_opacity_fade_out_start(self) -> None:
        """Test opacity at fade out start."""
        opacity = calculate_text_opacity(4.0, 1, 1, 2, 1)
        assert opacity == 1.0

    def test_opacity_fade_out_middle(self) -> None:
        """Test opacity at fade out middle."""
        opacity = calculate_text_opacity(4.5, 1, 1, 2, 1)
        assert 0.0 < opacity < 1.0

    def test_opacity_fade_out_end(self) -> None:
        """Test opacity at fade out end."""
        opacity = calculate_text_opacity(5, 1, 1, 2, 1)
        assert opacity == 0.0

    def test_opacity_after_fade_out(self) -> None:
        """Test opacity after fade out."""
        opacity = calculate_text_opacity(10, 1, 1, 2, 1)
        assert opacity == 0.0

    def test_opacity_zero_durations(self) -> None:
        """Test with zero durations."""
        opacity = calculate_text_opacity(1, 1, 0, 0, 0)
        assert opacity == 0.0


class TestCalculateVisibleChars:
    """Test visible character calculation for typing effect."""

    def test_visible_chars_before_start(self) -> None:
        """Test visible chars before typing starts."""
        visible = calculate_visible_chars(0, 0, 1, 5, 1)
        assert visible == 0

    def test_visible_chars_during_fade_in(self) -> None:
        """Test visible chars during fade in."""
        visible = calculate_visible_chars(0.5, 0, 1, 5, 1)
        assert visible == 0

    def test_visible_chars_typing_start(self) -> None:
        """Test visible chars at typing start."""
        visible = calculate_visible_chars(1, 0, 1, 5, 1)
        assert visible == 0

    def test_visible_chars_typing_partial(self) -> None:
        """Test visible chars during typing."""
        visible = calculate_visible_chars(1.5, 0, 1, 5, 1)
        assert visible == 0  # 0.5 seconds * 1 char/sec = 0 chars (int)

    def test_visible_chars_one_per_second(self) -> None:
        """Test typing one character per second."""
        visible = calculate_visible_chars(2, 0, 1, 5, 1)
        assert visible == 1

    def test_visible_chars_multiple(self) -> None:
        """Test multiple characters visible."""
        visible = calculate_visible_chars(4, 0, 1, 5, 1)
        assert visible == 3

    def test_visible_chars_all_visible(self) -> None:
        """Test all characters visible."""
        visible = calculate_visible_chars(10, 0, 1, 5, 1)
        assert visible == 5

    def test_visible_chars_fast_typing(self) -> None:
        """Test fast typing speed."""
        visible = calculate_visible_chars(1.5, 0, 1, 10, 5)  # 5 chars/sec
        assert visible == 2

    def test_visible_chars_capped_at_total(self) -> None:
        """Test visible chars capped at total."""
        visible = calculate_visible_chars(100, 0, 1, 3, 1)
        assert visible == 3


class TestCalculateScaleFactor:
    """Test scale factor calculation for depth effect."""

    def test_scale_before_animation(self) -> None:
        """Test scale is 1.0 before start time."""
        scale = calculate_scale_factor(0, 1, 1, 2, 1, 0.5, True, "ease_in_out")
        assert scale == 1.0

    def test_scale_after_animation(self) -> None:
        """Test scale is 1.0 after animation completes."""
        scale = calculate_scale_factor(10, 1, 1, 2, 1, 0.5, True, "ease_in_out")
        assert scale == 1.0

    def test_scale_fade_in_start(self) -> None:
        """Test scale at fade in start."""
        # At start_time, should be at initial_scale
        scale = calculate_scale_factor(1, 1, 1, 2, 1, 0.5, True, "linear")
        assert scale == pytest.approx(0.5)

    def test_scale_fade_in_middle(self) -> None:
        """Test scale at fade in middle."""
        # Linear: at 0.5s into 1s fade in, should be at 0.75 scale
        scale = calculate_scale_factor(1.5, 1, 1, 2, 1, 0.5, True, "linear")
        assert scale == pytest.approx(0.75)

    def test_scale_fade_in_end(self) -> None:
        """Test scale at fade in end."""
        # Should reach full scale (1.0) at end of fade in
        scale = calculate_scale_factor(2, 1, 1, 2, 1, 0.5, True, "linear")
        assert scale == pytest.approx(1.0)

    def test_scale_display_phase(self) -> None:
        """Test scale during display phase."""
        scale = calculate_scale_factor(2.5, 1, 1, 2, 1, 0.5, True, "linear")
        assert scale == pytest.approx(1.0)

    def test_scale_display_end(self) -> None:
        """Test scale at display end."""
        scale = calculate_scale_factor(4, 1, 1, 2, 1, 0.5, True, "linear")
        assert scale == pytest.approx(1.0)

    def test_scale_fade_out_start(self) -> None:
        """Test scale at fade out start."""
        scale = calculate_scale_factor(4.0, 1, 1, 2, 1, 0.5, True, "linear")
        assert scale == pytest.approx(1.0)

    def test_scale_fade_out_middle(self) -> None:
        """Test scale at fade out middle."""
        # Linear: at 0.5s into 1s fade out, should be at 0.75 scale
        scale = calculate_scale_factor(4.5, 1, 1, 2, 1, 0.5, True, "linear")
        assert scale == pytest.approx(0.75)

    def test_scale_fade_out_end(self) -> None:
        """Test scale at fade out end."""
        # Should return to initial_scale (0.5) just before animation ends
        scale = calculate_scale_factor(4.99, 1, 1, 2, 1, 0.5, True, "linear")
        assert scale == pytest.approx(0.501, rel=0.01)  # ~0.5 at end of fade out

    def test_scale_fade_out_disabled(self) -> None:
        """Test scale with fade out effect disabled."""
        # With apply_to_fade_out=False, should remain at 1.0 during fade out
        scale = calculate_scale_factor(4.5, 1, 1, 2, 1, 0.5, False, "linear")
        assert scale == pytest.approx(1.0)

    def test_scale_with_different_initial_scale(self) -> None:
        """Test with different initial scale value."""
        # Linear: at 0.5s into 1s fade in with 0.2 initial scale
        scale = calculate_scale_factor(1.5, 1, 1, 2, 1, 0.2, True, "linear")
        assert scale == pytest.approx(0.6)  # 0.2 + (1.0 - 0.2) * 0.5

    def test_scale_easing_linear(self) -> None:
        """Test linear easing."""
        scale = calculate_scale_factor(1.5, 1, 1, 2, 1, 0.5, True, "linear")
        assert scale == pytest.approx(0.75)

    def test_scale_easing_ease_in(self) -> None:
        """Test ease-in easing (quadratic)."""
        # At 0.5 progress, ease_in gives t^2 = 0.25
        scale = calculate_scale_factor(1.5, 1, 1, 2, 1, 0.5, True, "ease_in")
        # scale = 0.5 + (1.0 - 0.5) * 0.25 = 0.5 + 0.125 = 0.625
        assert scale == pytest.approx(0.625)

    def test_scale_easing_ease_out(self) -> None:
        """Test ease-out easing."""
        # At 0.5 progress, ease_out gives 1 - (1-0.5)^2 = 1 - 0.25 = 0.75
        scale = calculate_scale_factor(1.5, 1, 1, 2, 1, 0.5, True, "ease_out")
        # scale = 0.5 + (1.0 - 0.5) * 0.75 = 0.5 + 0.375 = 0.875
        assert scale == pytest.approx(0.875)

    def test_scale_easing_ease_in_out(self) -> None:
        """Test ease-in-out easing."""
        # At 0.5 progress, ease_in_out is at pivot, returns 0.5
        scale = calculate_scale_factor(1.5, 1, 1, 2, 1, 0.5, True, "ease_in_out")
        # scale = 0.5 + (1.0 - 0.5) * 0.5 = 0.75
        assert scale == pytest.approx(0.75)

    def test_scale_zero_fade_in_duration(self) -> None:
        """Test with zero fade in duration."""
        # With 0 duration, at start_time should jump to full scale
        scale = calculate_scale_factor(1, 1, 0, 2, 1, 0.5, True, "linear")
        # 0 / 0 would be problematic, but code should handle gracefully
        assert scale >= 0.5 and scale <= 1.0

    def test_scale_symmetry_fade_in_and_out(self) -> None:
        """Test that fade out mirrors fade in."""
        # Fade in at 0.25 progress (1.25s into 1s fade at 1s start)
        scale_in = calculate_scale_factor(1.25, 1, 1, 2, 1, 0.5, True, "linear")
        # Fade out at 0.75 progress (4.75s into 1s fade out starting at 4s)
        scale_out = calculate_scale_factor(4.75, 1, 1, 2, 1, 0.5, True, "linear")
        # Due to mirroring, these should be different - out should be shrinking
        assert scale_in == pytest.approx(0.625)
        assert scale_out == pytest.approx(0.625)
