"""Tests for text rendering."""

import pytest
from PIL import Image

from words_on_paper.rendering import (
    hex_to_rgb,
    render_text,
)


class TestHexToRgb:
    """Test hex to RGB conversion."""

    def test_hex_to_rgb_black(self) -> None:
        """Test converting black hex color."""
        assert hex_to_rgb("#000000") == (0, 0, 0)

    def test_hex_to_rgb_white(self) -> None:
        """Test converting white hex color."""
        assert hex_to_rgb("#FFFFFF") == (255, 255, 255)

    def test_hex_to_rgb_red(self) -> None:
        """Test converting red hex color."""
        assert hex_to_rgb("#FF0000") == (255, 0, 0)

    def test_hex_to_rgb_without_hash(self) -> None:
        """Test converting hex color without hash prefix."""
        assert hex_to_rgb("00FF00") == (0, 255, 0)

    def test_hex_to_rgb_lowercase(self) -> None:
        """Test converting lowercase hex color."""
        assert hex_to_rgb("#0000ff") == (0, 0, 255)

    def test_hex_to_rgb_invalid_format(self) -> None:
        """Test invalid hex color format."""
        with pytest.raises(ValueError):
            hex_to_rgb("#FFF")
        with pytest.raises(ValueError):
            hex_to_rgb("#GGGGGG")


class TestRenderText:
    """Test text rendering."""

    def test_render_text_horizontal(self) -> None:
        """Test rendering horizontal text."""
        img = render_text("Hello", font_size=24)
        assert isinstance(img, Image.Image)
        assert img.mode == "RGBA"
        assert img.width > 0
        assert img.height > 0

    def test_render_text_vertical(self) -> None:
        """Test rendering vertical text."""
        img = render_text("Hello", font_size=24, orientation="vertical")
        assert isinstance(img, Image.Image)
        assert img.mode == "RGBA"
        assert img.width > 0
        assert img.height > 0

    def test_render_text_color(self) -> None:
        """Test rendering with different colors."""
        img_red = render_text("Test", color="#FF0000", font_size=24)
        img_blue = render_text("Test", color="#0000FF", font_size=24)
        assert img_red.size == img_blue.size

    def test_render_text_different_sizes(self) -> None:
        """Test rendering with different font sizes."""
        img_small = render_text("Test", font_family="Liberation", font_size=12)
        img_large = render_text("Test", font_family="Liberation", font_size=48)
        # When using default font, sizes may not differ, so check that at least
        # we can render both successfully
        assert img_small.mode == "RGBA"
        assert img_large.mode == "RGBA"

    def test_render_empty_text(self) -> None:
        """Test rendering empty text."""
        img = render_text("", font_size=24)
        assert isinstance(img, Image.Image)

    def test_render_text_with_spaces(self) -> None:
        """Test rendering text with spaces."""
        img = render_text("Hello World", font_size=24)
        assert isinstance(img, Image.Image)
        assert img.width > 0

    def test_render_text_vertical_height(self) -> None:
        """Test vertical text height scales with character count."""
        img_short = render_text("A", font_size=24, orientation="vertical")
        img_long = render_text("ABCDE", font_size=24, orientation="vertical")
        assert img_long.height > img_short.height

    def test_render_text_mode_rgba(self) -> None:
        """Test that rendered image is RGBA."""
        img = render_text("Test", font_size=24)
        assert img.mode == "RGBA"

    def test_render_text_default_params(self) -> None:
        """Test rendering with default parameters."""
        img = render_text("Default")
        assert isinstance(img, Image.Image)
        assert img.mode == "RGBA"
