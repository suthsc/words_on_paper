"""Text to image rendering."""

from __future__ import annotations

from PIL import Image, ImageDraw

from words_on_paper.rendering.fonts import load_font


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
    rgb_color = _hex_to_rgb(color)

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

    # Calculate width (width of widest character)
    char_widths = []
    for char in text:
        bbox = dummy_draw.textbbox((0, 0), char, font=font)
        char_widths.append(bbox[2] - bbox[0])

    max_width = max(char_widths) if char_widths else 0

    # Calculate height (sum of all character heights with padding)
    char_spacing = 15  # Vertical spacing between characters
    char_height: int | None = None
    total_height: int = 0
    for char in text:
        bbox = dummy_draw.textbbox((0, 0), char, font=font)
        h = int(bbox[3] - bbox[1])
        if char_height is None:
            char_height = h
        total_height += h + char_spacing

    padding = 30  # Consistent padding for descenders
    width = int(max_width + 2 * padding)
    height = int(total_height + 2 * padding)

    # Create the image
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw characters vertically, centered horizontally
    char_spacing = 15  # Vertical spacing between characters
    y_pos = padding
    for char in text:
        bbox = dummy_draw.textbbox((0, 0), char, font=font)
        char_w = bbox[2] - bbox[0]
        char_h = bbox[3] - bbox[1]
        # Center character horizontally within max_width
        x_offset = padding + (max_width - char_w) // 2
        draw.text((x_offset, y_pos), char, font=font, fill=(*color, 255))
        y_pos += char_h + char_spacing

    return img


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """
    Convert hex color to RGB tuple.

    Args:
        hex_color: Color in hex format (#RRGGBB)

    Returns:
        (R, G, B) tuple with values 0-255
    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)
    except ValueError:
        raise ValueError(f"Invalid hex color: {hex_color}") from None
