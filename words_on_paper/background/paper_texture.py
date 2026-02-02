"""Paper texture generation."""

from __future__ import annotations

import numpy as np
from PIL import Image

from words_on_paper.utils.color import hex_to_rgb


def generate_background(
    width: int,
    height: int,
    color: str = "#FFFFFF",
    texture_type: str = "paper",
    texture_intensity: float = 0.05,
) -> Image.Image:
    """
    Generate a background image with optional paper texture.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        color: Background color in hex format (#RRGGBB)
        texture_type: Type of texture ("paper" or "solid")
        texture_intensity: Texture intensity from 0.0 to 1.0

    Returns:
        PIL Image with background
    """
    rgb = hex_to_rgb(color)

    if texture_type == "solid" or texture_intensity == 0:
        return _create_solid_background(width, height, rgb)
    else:
        return _create_textured_background(width, height, rgb, texture_intensity)


def _create_solid_background(
    width: int, height: int, rgb: tuple[int, int, int]
) -> Image.Image:
    """Create a solid color background."""
    return Image.new("RGB", (width, height), rgb)


def _create_textured_background(
    width: int,
    height: int,
    rgb: tuple[int, int, int],
    intensity: float,
) -> Image.Image:
    """Create a background with paper texture."""
    # Create base image with solid color
    img_array = np.full((height, width, 3), rgb, dtype=np.uint8)

    # Generate Perlin-like noise for texture
    noise = _generate_noise(width, height, intensity)

    # Apply noise to image
    img_array = np.clip(img_array.astype(float) + noise, 0, 255).astype(np.uint8)

    return Image.fromarray(img_array, "RGB")


def _generate_noise(width: int, height: int, intensity: float) -> np.ndarray:
    """
    Generate noise for texture effect.

    Args:
        width: Noise width
        height: Noise height
        intensity: Noise intensity (0.0 to 1.0)

    Returns:
        Noise array (height, width, 3)
    """
    # Use simple Perlin-like noise by downsampling and upsampling
    scale = max(1, int(50 * (1 - intensity)))

    # Create random noise at smaller scale
    small_width = max(1, width // scale)
    small_height = max(1, height // scale)

    noise_small = np.random.uniform(-20, 20, (small_height, small_width, 3))

    # Upsample to full size using nearest neighbor
    noise_full = np.zeros((height, width, 3))
    for y in range(height):
        for x in range(width):
            src_y = min(y // scale, small_height - 1)
            src_x = min(x // scale, small_width - 1)
            noise_full[y, x] = noise_small[src_y, src_x]

    return noise_full * intensity
