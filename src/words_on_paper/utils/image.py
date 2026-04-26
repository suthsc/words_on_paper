"""Image utility functions."""

from PIL import Image


def ensure_rgba(img: Image.Image) -> Image.Image:
    """
    Ensure image is in RGBA mode, converting if necessary.

    Args:
        img: PIL Image

    Returns:
        Image in RGBA mode
    """
    if img.mode != "RGBA":
        return img.convert("RGBA")
    return img
