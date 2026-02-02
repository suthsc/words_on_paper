"""Tests for background generation."""

from PIL import Image

from words_on_paper.background.paper_texture import generate_background


class TestGenerateBackground:
    """Test background generation."""

    def test_generate_solid_background(self) -> None:
        """Test generating solid background."""
        img = generate_background(1920, 1080, "#FFFFFF", "solid")
        assert isinstance(img, Image.Image)
        assert img.size == (1920, 1080)
        assert img.mode == "RGB"

    def test_generate_paper_background(self) -> None:
        """Test generating paper textured background."""
        img = generate_background(1920, 1080, "#FFFFFF", "paper", 0.05)
        assert isinstance(img, Image.Image)
        assert img.size == (1920, 1080)
        assert img.mode == "RGB"

    def test_generate_background_different_colors(self) -> None:
        """Test background with different colors."""
        img_white = generate_background(100, 100, "#FFFFFF")
        img_black = generate_background(100, 100, "#000000")
        assert img_white.size == img_black.size

    def test_generate_background_zero_texture(self) -> None:
        """Test background with zero texture intensity."""
        img = generate_background(100, 100, "#FFFFFF", "paper", 0.0)
        assert isinstance(img, Image.Image)

    def test_generate_background_max_texture(self) -> None:
        """Test background with maximum texture intensity."""
        img = generate_background(100, 100, "#FFFFFF", "paper", 1.0)
        assert isinstance(img, Image.Image)

    def test_generate_background_small_size(self) -> None:
        """Test generating small background."""
        img = generate_background(10, 10, "#FF0000")
        assert img.size == (10, 10)

    def test_generate_background_large_size(self) -> None:
        """Test generating large background."""
        img = generate_background(3840, 2160, "#00FF00")
        assert img.size == (3840, 2160)

    def test_generate_background_default_params(self) -> None:
        """Test background with default parameters."""
        img = generate_background(100, 100)
        assert isinstance(img, Image.Image)
        assert img.mode == "RGB"
