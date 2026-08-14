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
    center_spacing: bool = False,
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
        center_spacing: If True, distribute spacing symmetrically around text center

    Returns:
        PIL Image with rendered text
    """
    font = load_font(font_family, font_size)
    rgb_color = hex_to_rgb(color)

    if orientation == "vertical":
        return _render_vertical(text, font, rgb_color, letter_spacing, center_spacing)
    else:
        return _render_horizontal(text, font, rgb_color, letter_spacing, center_spacing)


def get_text_dimensions(
    text: str,
    font_family: str = "Arial",
    font_size: int = 72,
    orientation: str = "horizontal",
    letter_spacing: float = 1.0,
    center_spacing: bool = False,
) -> tuple[int, int]:
    """
    Get text dimensions without rendering.

    Args:
        text: The text to measure
        font_family: Font family name
        font_size: Font size in pixels
        orientation: "horizontal" or "vertical"
        letter_spacing: Letter spacing multiplier (1.0 = normal)
        center_spacing: If True, assume centered spacing distribution

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
            text, font, direction, align, letter_spacing, center_spacing
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


def _spacing_multipliers(
    count: int, letter_spacing: float, center_spacing: bool
) -> list[float]:
    """
    Compute the per-character spacing multiplier to apply after each character.

    Args:
        count: Number of characters
        letter_spacing: Letter spacing multiplier
        center_spacing: If True, spacing is distributed symmetrically around center

    Returns:
        List of per-character spacing multipliers, length `count`
    """
    if not center_spacing:
        return [letter_spacing] * count

    center_pos = count / 2.0
    return [
        letter_spacing
        + (1.0 - letter_spacing)
        * min(abs(i - center_pos + 0.5) / (center_pos + 0.5), 1.0)
        for i in range(count)
    ]


def _sum_spaced_sizes(
    sizes: list[float], letter_spacing: float, center_spacing: bool
) -> float:
    """
    Sum per-character sizes with letter spacing applied between characters.

    The trailing spacing after the last character is removed, since spacing
    represents the gap between characters, not a trailing margin.
    """
    if not sizes:
        return 0.0

    spacings = _spacing_multipliers(len(sizes), letter_spacing, center_spacing)
    total = sum(size * spacing for size, spacing in zip(sizes, spacings))
    total -= sizes[-1] * spacings[-1] - sizes[-1]
    return total


def _calculate_spaced_dimensions(
    text: str,
    font,
    direction: str | None,
    align: str | None,
    letter_spacing: float,
    center_spacing: bool = False,
) -> tuple[float, float]:
    """
    Calculate dimensions for text with custom letter spacing.

    Args:
        text: Text to measure
        font: Loaded font object
        direction: Text direction ("ttb" for vertical, None for horizontal)
        align: Text alignment
        letter_spacing: Letter spacing multiplier
        center_spacing: If True, spacing is distributed symmetrically around center

    Returns:
        (width, height) tuple in pixels
    """
    dummy_img = Image.new("RGBA", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)

    char_widths = []
    char_heights = []
    for char in text:
        bbox = dummy_draw.textbbox((0, 0), char, font=font)
        char_widths.append(bbox[2] - bbox[0])
        char_heights.append(bbox[3] - bbox[1])

    if direction == "ttb":
        total_height = _sum_spaced_sizes(char_heights, letter_spacing, center_spacing)
        return max(char_widths, default=0.0), total_height
    else:
        total_width = _sum_spaced_sizes(char_widths, letter_spacing, center_spacing)
        return total_width, max(char_heights, default=0.0)


def _render_text(
    text: str,
    font,
    color: tuple[int, int, int],
    direction: str | None = None,
    align: str | None = None,
    letter_spacing: float = 1.0,
    center_spacing: bool = False,
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
        center_spacing: If True, distribute spacing symmetrically around text center

    Returns:
        PIL Image with rendered text
    """
    padding = 30
    dummy_img = Image.new("RGBA", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)

    # Calculate dimensions considering letter spacing
    if letter_spacing != 1.0:
        text_width, text_height = _calculate_spaced_dimensions(
            text, font, direction, align, letter_spacing, center_spacing
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
        if center_spacing:
            _draw_spaced_text_centered(
                draw,
                text,
                (padding - bbox[0], padding - bbox[1]),
                font,
                (*color, 255),
                direction,
                letter_spacing,
            )
        else:
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


def _draw_spaced_text_centered(
    draw,
    text: str,
    position: tuple[float, float],
    font,
    fill,
    direction: str | None,
    letter_spacing: float,
) -> None:
    """
    Draw text with centered letter spacing distribution.

    Distributes spacing symmetrically around text center: characters near the
    center maintain closer spacing, characters at edges have wider spacing.

    Args:
        draw: ImageDraw object
        text: Text to render
        position: Starting position (x, y)
        font: Loaded font object
        fill: Fill color (RGBA tuple)
        direction: Text direction ("ttb" for vertical, None for horizontal)
        letter_spacing: Letter spacing multiplier (center uses this as target)
    """
    if not text:
        return

    x_start, y_start = position
    center_pos = len(text) / 2.0

    if direction == "ttb":
        # Vertical text: position characters vertically with centered spacing
        char_heights = []
        dummy_img = Image.new("RGBA", (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)

        for char in text:
            bbox = dummy_draw.textbbox((0, 0), char, font=font)
            char_heights.append(bbox[3] - bbox[1])

        # Calculate positions from center outward
        y = y_start
        for i, char in enumerate(text):
            # Distance from center (0 at center, increases toward edges)
            dist_from_center = abs(i - center_pos + 0.5)
            # Interpolate spacing: closer to center = tighter (letter_spacing)
            # farther from center = looser (1.0)
            normalized_dist = min(dist_from_center / (center_pos + 0.5), 1.0)
            spacing = letter_spacing + (1.0 - letter_spacing) * normalized_dist

            draw.text((x_start, y), char, font=font, fill=fill, direction=direction)
            y += char_heights[i] * spacing
    else:
        # Horizontal text: position characters horizontally with centered spacing
        char_widths = []
        dummy_img = Image.new("RGBA", (1, 1))
        dummy_draw = ImageDraw.Draw(dummy_img)

        for char in text:
            bbox = dummy_draw.textbbox((0, 0), char, font=font)
            char_widths.append(bbox[2] - bbox[0])

        # Calculate positions from center outward
        x = x_start
        for i, char in enumerate(text):
            # Distance from center (0 at center, increases toward edges)
            dist_from_center = abs(i - center_pos + 0.5)
            # Interpolate spacing: closer to center = tighter (letter_spacing)
            # farther from center = looser (1.0)
            normalized_dist = min(dist_from_center / (center_pos + 0.5), 1.0)
            spacing = letter_spacing + (1.0 - letter_spacing) * normalized_dist

            draw.text((x, y_start), char, font=font, fill=fill)
            x += char_widths[i] * spacing


def _render_horizontal(
    text: str,
    font,
    color: tuple[int, int, int],
    letter_spacing: float = 1.0,
    center_spacing: bool = False,
) -> Image.Image:
    """Render text horizontally (left to right)."""
    return _render_text(
        text, font, color, letter_spacing=letter_spacing, center_spacing=center_spacing
    )


def _render_vertical(
    text: str,
    font,
    color: tuple[int, int, int],
    letter_spacing: float = 1.0,
    center_spacing: bool = False,
) -> Image.Image:
    """Render text vertically (top to bottom)."""
    return _render_text(
        text,
        font,
        color,
        direction="ttb",
        align="center",
        letter_spacing=letter_spacing,
        center_spacing=center_spacing,
    )
