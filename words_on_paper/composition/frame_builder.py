"""Frame building and composition."""

from __future__ import annotations

import random
from typing import Any

from PIL import Image

from words_on_paper.background import generate_background
from words_on_paper.composition.animator import (
    calculate_text_opacity,
    calculate_visible_chars,
)
from words_on_paper.composition.layer_manager import composite_layers
from words_on_paper.config.schema import TextSequence, VideoConfig
from words_on_paper.rendering.text_renderer import render_text
from words_on_paper.utils.color import hex_to_rgba


def build_frame(
    config: VideoConfig,
    current_time: float,
) -> Image.Image:
    """
    Build a single frame at the given time.

    Args:
        config: Video configuration
        current_time: Current time in seconds

    Returns:
        PIL Image for the frame
    """
    width = int(config.video["width"])
    height = int(config.video["height"])

    # Create background
    bg_config = config.background
    background = generate_background(
        width,
        height,
        bg_config.color,
        bg_config.type,
        bg_config.texture_intensity,
    )

    # Convert background to RGBA for compositing
    if background.mode != "RGBA":
        background = background.convert("RGBA")

    # Build layers from text sequences
    layers: list[tuple[Image.Image, int, int, int]] = []

    for text_seq in config.texts:
        layer_img, x, y = _render_text_layer(
            text_seq, current_time, int(width), int(height)
        )
        if layer_img is not None:
            layers.append((layer_img, x, y, text_seq.z_index))

    # Composite layers
    if layers:
        result = composite_layers(background, layers)
    else:
        result = background

    # Convert back to RGB for video output
    if result.mode == "RGBA":
        result = result.convert("RGB")

    return result


def _render_text_layer(
    text_seq: TextSequence,
    current_time: float,
    video_width: int,
    video_height: int,
) -> tuple[Image.Image | None | Any, int, int]:
    """
    Render a single text layer if it should be visible.

    Args:
        text_seq: Text sequence configuration
        current_time: Current time in seconds
        video_width: Video width in pixels
        video_height: Video height in pixels

    Returns:
        (layer_image, x, y) or (None, 0, 0) if not visible
    """
    # Calculate opacity
    opacity = calculate_text_opacity(
        current_time,
        text_seq.start_time,
        text_seq.fade_in_duration,
        text_seq.display_duration,
        text_seq.fade_out_duration,
    )

    # If fully transparent, skip
    if opacity <= 0:
        return None, 0, 0

    # Calculate visible characters for typing effect
    visible_char_count = len(text_seq.content)
    if text_seq.effects.typing.enabled:
        visible_char_count = calculate_visible_chars(
            current_time,
            text_seq.start_time,
            text_seq.fade_in_duration,
            len(text_seq.content),
            text_seq.effects.typing.chars_per_second,
        )

    # Render full text (for consistent positioning)
    full_text_img = render_text(
        text_seq.content,
        text_seq.font.family,
        text_seq.font.size,
        text_seq.font.color,
        text_seq.orientation,
    )

    # Calculate position BEFORE any cropping (based on full text dimensions)
    x, y = _calculate_position(
        text_seq.position,
        full_text_img.width,
        full_text_img.height,
        video_width,
        video_height,
        text_seq.content,
    )

    # For typing effect, clip to show only visible characters
    text_img = full_text_img
    if text_seq.effects.typing.enabled and visible_char_count < len(text_seq.content):
        # Render visible text to get its dimensions
        visible_text_img = render_text(
            text_seq.content[:visible_char_count],
            text_seq.font.family,
            text_seq.font.size,
            text_seq.font.color,
            text_seq.orientation,
        )
        # Crop the full text image to show only visible portion
        text_img = full_text_img.crop(
            (0, 0, visible_text_img.width, visible_text_img.height)
        )

    # Apply opacity
    if opacity < 1.0:
        text_img = _apply_opacity(text_img, opacity)

    # Apply drop shadow if enabled
    if text_seq.effects.drop_shadow.enabled:
        text_img = _apply_drop_shadow(text_img, text_seq.effects.drop_shadow)

    return text_img, x, y


def _apply_opacity(img: Image.Image, opacity: float) -> Image.Image:
    """Apply opacity to an image."""
    # Convert to RGBA if needed
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    # Apply opacity to alpha channel
    alpha = img.split()[3]
    alpha = alpha.point(lambda x: int(x * opacity))

    img.putalpha(alpha)
    return img


def _apply_drop_shadow(img: Image.Image, shadow_config) -> Image.Image:
    """Apply drop shadow effect to an image."""
    from PIL import ImageFilter

    # Ensure RGBA mode
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    # Get shadow color with alpha
    shadow_rgba = hex_to_rgba(shadow_config.color)

    # Create shadow layer
    # shadow = Image.new("RGBA", img.size, (0, 0, 0, 0))

    # Create blurred version of text
    alpha = img.split()[3]
    shadow_layer = Image.new(
        "RGBA",
        img.size,
        (shadow_rgba[0], shadow_rgba[1], shadow_rgba[2], 0),
    )
    shadow_layer.putalpha(alpha)

    # Blur shadow
    if shadow_config.blur_radius > 0:
        shadow_layer = shadow_layer.filter(
            ImageFilter.GaussianBlur(shadow_config.blur_radius)
        )

    # Create result with shadow
    result = Image.new(
        "RGBA",
        (
            img.width + shadow_config.offset_x,
            img.height + shadow_config.offset_y,
        ),
        (0, 0, 0, 0),
    )

    # Paste shadow
    result.paste(
        shadow_layer, (shadow_config.offset_x, shadow_config.offset_y), shadow_layer
    )

    # Paste text on top
    result.paste(img, (0, 0), img)

    return result


def _calculate_position(
    position_config,
    text_width: int,
    text_height: int,
    video_width: int,
    video_height: int,
    text_content: str = "",
) -> tuple[int, int]:
    """
    Calculate x, y position based on positioning mode.

    Args:
        position_config: Position configuration
        text_width: Text image width
        text_height: Text image height
        video_width: Video width
        video_height: Video height
        text_content: Text content for deterministic random seeding

    Returns:
        (x, y) position
    """
    if position_config.mode == "absolute":
        x = int(position_config.x or 0)
        y = int(position_config.y or 0)
    elif position_config.mode == "relative":
        x = int(video_width * (position_config.x or 0))
        y = int(video_height * (position_config.y or 0))
    elif position_config.mode == "random":
        # Use text content for deterministic random positioning
        rng = random.Random(text_content)
        # Constrain to 20-80% of available space, but allow full range if text is too large
        x_min = int(video_width * 0.2)
        x_max = int(video_width * 0.8 - text_width)
        y_min = int(video_height * 0.2)
        y_max = int(video_height * 0.8 - text_height)

        # If text is larger than available space, use full range
        if x_max < x_min:
            x_min = 0
            x_max = max(0, video_width - text_width)
        if y_max < y_min:
            y_min = 0
            y_max = max(0, video_height - text_height)

        x = rng.randint(x_min, x_max) if x_max >= x_min else x_min
        y = rng.randint(y_min, y_max) if y_max >= y_min else y_min
    else:  # center
        x = (video_width - text_width) // 2
        y = (video_height - text_height) // 2

    return x, y
