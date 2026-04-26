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


def get_text_dimensions(
    text: str,
    font_family: str = "Arial",
    font_size: int = 72,
    orientation: str = "horizontal",
) -> tuple[int, int]:
    """
    Get text dimensions without rendering.

    Args:
        text: The text to measure
        font_family: Font family name
        font_size: Font size in pixels
        orientation: "horizontal" or "vertical"

    Returns:
        (width, height) tuple in pixels
    """
    font = load_font(font_family, font_size)
    dummy_img = Image.new("RGBA", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)

    padding = 30
    direction = "ttb" if orientation == "vertical" else None
    align = "center" if orientation == "vertical" else None

    bbox = dummy_draw.textbbox(
        (0, 0), text, font=font, direction=direction, align=align
    )
    width = int(bbox[2] - bbox[0] + 2 * padding)
    height = int(bbox[3] - bbox[1] + 2 * padding)

    return width, height


def _render_text(
    text: str,
    font,
    color: tuple[int, int, int],
    direction: str | None = None,
    align: str | None = None,
) -> Image.Image:
    """
    Render text to image with optional direction and alignment.

    Args:
        text: Text to render
        font: Loaded font object
        color: RGB color tuple
        direction: Text direction ("ttb" for vertical, None for horizontal)
        align: Text alignment ("center" for vertical, None for horizontal)

    Returns:
        PIL Image with rendered text
    """
    padding = 30
    dummy_img = Image.new("RGBA", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)

    bbox = dummy_draw.textbbox(
        (0, 0), text, font=font, direction=direction, align=align
    )
    # bbox is (left, top, right, bottom) - top/left can be negative due to ascenders
    width = int(bbox[2] - bbox[0] + 2 * padding)
    height = int(bbox[3] - bbox[1] + 2 * padding)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Offset by -bbox[0] and -bbox[1] to position text at correct location with padding
    draw.text(
        (padding - bbox[0], padding - bbox[1]),
        text,
        font=font,
        fill=(*color, 255),
        direction=direction,
        align=align,
    )

    return img


def _render_horizontal(text: str, font, color: tuple[int, int, int]) -> Image.Image:
    """Render text horizontally (left to right)."""
    return _render_text(text, font, color)


def _render_vertical(text: str, font, color: tuple[int, int, int]) -> Image.Image:
    """Render text vertically (top to bottom)."""
    return _render_text(text, font, color, direction="ttb", align="center")
