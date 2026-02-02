"""Color utilities."""


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """
    Convert hex color to RGB tuple.

    Args:
        hex_color: Color in hex format (#RRGGBB or RRGGBB)

    Returns:
        (R, G, B) tuple with values 0-255

    Raises:
        ValueError: If hex color format is invalid
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


def hex_to_rgba(hex_color: str) -> tuple[int, int, int, int]:
    """
    Convert hex color to RGBA tuple.

    Args:
        hex_color: Color in hex format (#RRGGBBAA, #RRGGBB, RRGGBBAA, or RRGGBB)

    Returns:
        (R, G, B, A) tuple with values 0-255

    Raises:
        ValueError: If hex color format is invalid
    """
    hex_color = hex_color.lstrip("#")

    if len(hex_color) == 6:
        r, g, b = hex_to_rgb(hex_color)
        return (r, g, b, 255)
    elif len(hex_color) == 8:
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            a = int(hex_color[6:8], 16)
            return (r, g, b, a)
        except ValueError:
            raise ValueError(f"Invalid hex color: {hex_color}") from None
    else:
        raise ValueError(f"Invalid hex color: {hex_color}") from None


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convert RGB values to hex color.

    Args:
        r: Red component (0-255)
        g: Green component (0-255)
        b: Blue component (0-255)

    Returns:
        Hex color string (#RRGGBB)

    Raises:
        ValueError: If values are out of range
    """
    if not all(0 <= v <= 255 for v in (r, g, b)):
        raise ValueError("RGB values must be in range 0-255")

    return f"#{r:02X}{g:02X}{b:02X}"
