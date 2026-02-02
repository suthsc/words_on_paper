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
    # Use size directly as pixels
    pixel_size = int(size)

    # Try different font file variations (prefer .ttf over .ttc)
    font_variations = [
        f"{family}.ttf",
        f"{family}Regular.ttf",
        f"{family} Regular.ttf",
        f"{family}HB.ttc",
        f"{family}.ttc",
    ]

    # Common font paths for different systems
    font_base_paths = [
        # macOS
        Path("/Library/Fonts"),
        Path("/System/Library/Fonts"),
        Path("/System/Library/Fonts/Supplemental"),
        Path.home() / "Library/Fonts",
        # Linux
        Path("/usr/share/fonts/truetype"),
        Path("/usr/share/fonts/truetype/liberation"),
        # Windows
        Path("C:/Windows/Fonts"),
    ]

    # Try to find the font file
    for base_path in font_base_paths:
        for font_file in font_variations:
            font_path = base_path / font_file
            if font_path.exists():
                try:
                    font = ImageFont.truetype(str(font_path), pixel_size)
                    return font
                except Exception:
                    continue

    # Try Helvetica as fallback for Arial
    if family.lower() == "arial":
        try:
            return load_font("Helvetica", size)
        except Exception:
            pass

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
