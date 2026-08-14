"""Paper texture generation."""

from __future__ import annotations

from functools import lru_cache

import numpy as np
from PIL import Image

from words_on_paper.utils.color import hex_to_rgb


@lru_cache(maxsize=None)
def generate_background(
    width: int,
    height: int,
    color: str = "#FFFFFF",
    texture_type: str = "paper",
    texture_intensity: float = 0.05,
) -> Image.Image:
    """
    Generate a background image with optional paper texture.

    Cached per (width, height, color, texture_type, texture_intensity) since
    the same static background is otherwise rebuilt on every frame. Callers
    must not mutate the returned image in place — copy it first.

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

    # Create random noise at smaller scale (use ceil to ensure upsampled result is large enough)
    import math

    small_width = max(1, math.ceil(width / scale))
    small_height = max(1, math.ceil(height / scale))

    noise_small = np.random.uniform(-20, 20, (small_height, small_width, 3))

    # Upsample to full size using vectorized repeat operations (10-100x faster than loops)
    noise_full = np.repeat(np.repeat(noise_small, scale, axis=0), scale, axis=1)

    # Trim to exact dimensions
    noise_full = noise_full[:height, :width, :]

    return noise_full * intensity
