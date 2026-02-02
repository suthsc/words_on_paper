"""Tests for color utilities."""

import pytest

from words_on_paper.utils.color import (
    hex_to_rgb,
    hex_to_rgba,
    rgb_to_hex,
)


class TestHexToRgb:
    """Test hex to RGB conversion."""

    def test_hex_to_rgb_black(self) -> None:
        """Test converting black."""
        assert hex_to_rgb("#000000") == (0, 0, 0)

    def test_hex_to_rgb_white(self) -> None:
        """Test converting white."""
        assert hex_to_rgb("#FFFFFF") == (255, 255, 255)

    def test_hex_to_rgb_red(self) -> None:
        """Test converting red."""
        assert hex_to_rgb("#FF0000") == (255, 0, 0)

    def test_hex_to_rgb_green(self) -> None:
        """Test converting green."""
        assert hex_to_rgb("#00FF00") == (0, 255, 0)

    def test_hex_to_rgb_blue(self) -> None:
        """Test converting blue."""
        assert hex_to_rgb("#0000FF") == (0, 0, 255)

    def test_hex_to_rgb_without_hash(self) -> None:
        """Test hex without hash prefix."""
        assert hex_to_rgb("FF0000") == (255, 0, 0)

    def test_hex_to_rgb_lowercase(self) -> None:
        """Test lowercase hex."""
        assert hex_to_rgb("#ff0000") == (255, 0, 0)

    def test_hex_to_rgb_invalid_short(self) -> None:
        """Test invalid short hex."""
        with pytest.raises(ValueError):
            hex_to_rgb("#FFF")

    def test_hex_to_rgb_invalid_chars(self) -> None:
        """Test invalid hex characters."""
        with pytest.raises(ValueError):
            hex_to_rgb("#GGGGGG")


class TestHexToRgba:
    """Test hex to RGBA conversion."""

    def test_hex_to_rgba_6_digit(self) -> None:
        """Test 6-digit hex converts to RGBA with full alpha."""
        assert hex_to_rgba("#FF0000") == (255, 0, 0, 255)

    def test_hex_to_rgba_8_digit(self) -> None:
        """Test 8-digit hex with alpha."""
        assert hex_to_rgba("#FF000080") == (255, 0, 0, 128)

    def test_hex_to_rgba_full_alpha(self) -> None:
        """Test 8-digit hex with full alpha."""
        assert hex_to_rgba("#FF0000FF") == (255, 0, 0, 255)

    def test_hex_to_rgba_zero_alpha(self) -> None:
        """Test 8-digit hex with zero alpha."""
        assert hex_to_rgba("#FF000000") == (255, 0, 0, 0)

    def test_hex_to_rgba_invalid_length(self) -> None:
        """Test invalid hex length for RGBA."""
        with pytest.raises(ValueError):
            hex_to_rgba("#FFF")


class TestRgbToHex:
    """Test RGB to hex conversion."""

    def test_rgb_to_hex_black(self) -> None:
        """Test black to hex."""
        assert rgb_to_hex(0, 0, 0) == "#000000"

    def test_rgb_to_hex_white(self) -> None:
        """Test white to hex."""
        assert rgb_to_hex(255, 255, 255) == "#FFFFFF"

    def test_rgb_to_hex_red(self) -> None:
        """Test red to hex."""
        assert rgb_to_hex(255, 0, 0) == "#FF0000"

    def test_rgb_to_hex_invalid_negative(self) -> None:
        """Test invalid negative values."""
        with pytest.raises(ValueError):
            rgb_to_hex(-1, 0, 0)

    def test_rgb_to_hex_invalid_overflow(self) -> None:
        """Test invalid overflow values."""
        with pytest.raises(ValueError):
            rgb_to_hex(256, 0, 0)
