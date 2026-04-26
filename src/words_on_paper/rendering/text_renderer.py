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
    letter_spacing: float = 1.0,
) -> Image.Image:
    """
    Render text to a PIL Image.

    Args:
        text: The text to render
        font_family: Font family name
        font_size: Font size in pixels
        color: Text color in hex format (#RRGGBB)
        orientation: "horizontal" or "vertical"
        letter_spacing: Letter spacing multiplier (1.0 = normal, <1.0 = closer, >1.0 = wider)

    Returns:
        PIL Image with rendered text
    """
    font = load_font(font_family, font_size)
    rgb_color = hex_to_rgb(color)

    if orientation == "vertical":
        return _render_vertical(text, font, rgb_color, letter_spacing)
    else:
        return _render_horizontal(text, font, rgb_color, letter_spacing)


def get_text_dimensions(
    text: str,
    font_family: str = "Arial",
    font_size: int = 72,
    orientation: str = "horizontal",
    letter_spacing: float = 1.0,
) -> tuple[int, int]:
    """
    Get text dimensions without rendering.

    Args:
        text: The text to measure
        font_family: Font family name
        font_size: Font size in pixels
        orientation: "horizontal" or "vertical"
        letter_spacing: Letter spacing multiplier (1.0 = normal)

    Returns:
        (width, height) tuple in pixels
    """
    font = load_font(font_family, font_size)
    dummy_img = Image.new("RGBA", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)

    padding = 30
    direction = "ttb" if orientation == "vertical" else None
    align = "center" if orientation == "vertical" else None

    # For letter-spacing calculations, measure with adjusted spacing
    if letter_spacing != 1.0:
        width, height = _calculate_spaced_dimensions(
            text, font, direction, align, letter_spacing
        )
    else:
        bbox = dummy_draw.textbbox(
            (0, 0), text, font=font, direction=direction, align=align
        )
        width = int(bbox[2] - bbox[0])
        height = int(bbox[3] - bbox[1])

    width = int(width + 2 * padding)
    height = int(height + 2 * padding)

    return width, height


def _calculate_spaced_dimensions(
    text: str,
    font,
    direction: str | None,
    align: str | None,
    letter_spacing: float,
) -> tuple[float, float]:
    """
    Calculate dimensions for text with custom letter spacing.

    Args:
        text: Text to measure
        font: Loaded font object
        direction: Text direction ("ttb" for vertical, None for horizontal)
        align: Text alignment
        letter_spacing: Letter spacing multiplier

    Returns:
        (width, height) tuple in pixels
    """
    dummy_img = Image.new("RGBA", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)

    if direction == "ttb":
        # Vertical text: measure each character's height, sum with spacing
        total_height = 0.0
        max_width = 0.0
        for char in text:
            bbox = dummy_draw.textbbox((0, 0), char, font=font)
            char_width = bbox[2] - bbox[0]
            char_height = bbox[3] - bbox[1]
            total_height += char_height * letter_spacing
            max_width = max(max_width, char_width)
        # Adjust for spacing: remove extra spacing after last character
        if text:
            total_height -= char_height * letter_spacing - char_height
        return max_width, total_height
    else:
        # Horizontal text: measure each character's width, sum with spacing
        total_width = 0.0
        max_height = 0.0
        for char in text:
            bbox = dummy_draw.textbbox((0, 0), char, font=font)
            char_width = bbox[2] - bbox[0]
            char_height = bbox[3] - bbox[1]
            total_width += char_width * letter_spacing
            max_height = max(max_height, char_height)
        # Adjust for spacing: remove extra spacing after last character
        if text:
            total_width -= char_width * letter_spacing - char_width
        return total_width, max_height


def _render_text(
    text: str,
    font,
    color: tuple[int, int, int],
    direction: str | None = None,
    align: str | None = None,
    letter_spacing: float = 1.0,
) -> Image.Image:
    """
    Render text to image with optional direction and alignment and letter spacing.

    Args:
        text: Text to render
        font: Loaded font object
        color: RGB color tuple
        direction: Text direction ("ttb" for vertical, None for horizontal)
        align: Text alignment ("center" for vertical, None for horizontal)
        letter_spacing: Letter spacing multiplier (1.0 = normal)

    Returns:
        PIL Image with rendered text
    """
    padding = 30
    dummy_img = Image.new("RGBA", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)

    # Calculate dimensions considering letter spacing
    if letter_spacing != 1.0:
        text_width, text_height = _calculate_spaced_dimensions(
            text, font, direction, align, letter_spacing
        )
        # Get baseline bbox for positioning
        bbox = dummy_draw.textbbox(
            (0, 0),
            text[0] if text else "A",
            font=font,
            direction=direction,
            align=align,
        )
    else:
        bbox = dummy_draw.textbbox(
            (0, 0), text, font=font, direction=direction, align=align
        )
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

    width = int(text_width + 2 * padding)
    height = int(text_height + 2 * padding)

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if letter_spacing != 1.0:
        _draw_spaced_text(
            draw,
            text,
            (padding - bbox[0], padding - bbox[1]),
            font,
            (*color, 255),
            direction,
            letter_spacing,
        )
    else:
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


def _draw_spaced_text(
    draw,
    text: str,
    position: tuple[float, float],
    font,
    fill,
    direction: str | None,
    letter_spacing: float,
) -> None:
    """
    Draw text with custom letter spacing by rendering each character individually.

    Args:
        draw: ImageDraw object
        text: Text to render
        position: Starting position (x, y)
        font: Loaded font object
        fill: Fill color (RGBA tuple)
        direction: Text direction ("ttb" for vertical, None for horizontal)
        letter_spacing: Letter spacing multiplier
    """
    x, y = position

    if direction == "ttb":
        # Vertical text: position characters vertically
        for char in text:
            draw.text((x, y), char, font=font, fill=fill, direction=direction)
            # Get character height for spacing
            dummy_img = Image.new("RGBA", (1, 1))
            dummy_draw = ImageDraw.Draw(dummy_img)
            bbox = dummy_draw.textbbox((0, 0), char, font=font)
            char_height = bbox[3] - bbox[1]
            y += char_height * letter_spacing
    else:
        # Horizontal text: position characters horizontally
        for char in text:
            draw.text((x, y), char, font=font, fill=fill)
            # Get character width for spacing
            dummy_img = Image.new("RGBA", (1, 1))
            dummy_draw = ImageDraw.Draw(dummy_img)
            bbox = dummy_draw.textbbox((0, 0), char, font=font)
            char_width = bbox[2] - bbox[0]
            x += char_width * letter_spacing


def _render_horizontal(
    text: str, font, color: tuple[int, int, int], letter_spacing: float = 1.0
) -> Image.Image:
    """Render text horizontally (left to right)."""
    return _render_text(text, font, color, letter_spacing=letter_spacing)


def _render_vertical(
    text: str, font, color: tuple[int, int, int], letter_spacing: float = 1.0
) -> Image.Image:
    """Render text vertically (top to bottom)."""
    return _render_text(
        text,
        font,
        color,
        direction="ttb",
        align="center",
        letter_spacing=letter_spacing,
    )
