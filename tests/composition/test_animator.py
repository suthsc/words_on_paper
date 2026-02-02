"""Tests for animation calculations."""

from words_on_paper.composition.animator import (
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
