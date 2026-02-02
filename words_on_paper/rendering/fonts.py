"""Font loading and management."""

from __future__ import annotations

from pathlib import Path

from PIL import ImageFont


def load_font(family: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """
    Load a TrueType font by family name and size.

    Attempts to find the font in common system locations.
    Falls back to default font if not found.

    Args:
        family: Font family name (e.g., "Arial", "Courier")
        size: Font size in pixels

    Returns:
        PIL ImageFont object
    """
    # Common font paths for different systems
    font_paths = [
        # macOS
        Path("/Library/Fonts") / f"{family}.ttf",
        Path("/System/Library/Fonts") / f"{family}.ttf",
        Path.home() / "Library/Fonts" / f"{family}.ttf",
        # Linux
        Path("/usr/share/fonts/truetype") / family.lower() / f"{family}.ttf",
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
        # Windows
        Path("C:/Windows/Fonts") / f"{family}.ttf",
    ]

    # Try to find the font file
    for font_path in font_paths:
        if font_path.exists():
            try:
                return ImageFont.truetype(str(font_path), size)
            except Exception:
                continue

    # Fallback to default font
    return ImageFont.load_default()


def get_fallback_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """
    Get a fallback font (Liberation Sans on Linux, similar on other systems).

    Args:
        size: Font size in pixels

    Returns:
        PIL ImageFont object
    """
    try:
        return load_font("Liberation", size)
    except Exception:
        return ImageFont.load_default()
