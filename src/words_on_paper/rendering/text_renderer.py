"""Text to image rendering."""

from __future__ import annotations

from PIL import Image, ImageDraw

from words_on_paper.rendering.fonts import load_font
from words_on_paper.utils import hex_to_rgb


def render_text(
    text: str,
    font_family: str = "Arial",
    font_size: int = 72,
    color: str = "#000000",
    orientation: str = "horizontal",
) -> Image.Image:
    """
    Render text to a PIL Image.

    Args:
        text: The text to render
        font_family: Font family name
        font_size: Font size in pixels
        color: Text color in hex format (#RRGGBB)
        orientation: "horizontal" or "vertical"

    Returns:
        PIL Image with rendered text
    """
    font = load_font(font_family, font_size)
    rgb_color = hex_to_rgb(color)

    if orientation == "vertical":
        return _render_vertical(text, font, rgb_color)
    else:
        return _render_horizontal(text, font, rgb_color)


def _render_horizontal(text: str, font, color: tuple[int, int, int]) -> Image.Image:
    """Render text horizontally (left to right)."""
    # Create a dummy image to calculate text dimensions
    dummy_img = Image.new("RGBA", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)

    bbox = dummy_draw.textbbox((0, 0), text, font=font)
    padding = 30  # Increased padding for descenders
    width = int(bbox[2] - bbox[0] + 2 * padding)
    height = int(bbox[3] - bbox[1] + 2 * padding)

    # Create the actual image
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw the text with padding offset
    draw.text((padding, padding), text, font=font, fill=(*color, 255))

    return img


def _render_vertical(text: str, font, color: tuple[int, int, int]) -> Image.Image:
    """Render text vertically (top to bottom)."""
    # Calculate dimensions for vertical text
    dummy_img = Image.new("RGBA", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)

    bbox = dummy_draw.textbbox((0, 0), text, font=font, direction="ttb", align="center")
    padding = 30  # Increased padding for descenders
    width = int(bbox[2] - bbox[0] + 2 * padding)
    height = int(bbox[3] - bbox[1] + 2 * padding)

    # Create the image
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.text(
        (padding, padding),
        text,
        font=font,
        fill=(*color, 255),
        direction="ttb",
        align="center",
    )

    return img
