"""Frame building and composition."""

from __future__ import annotations

import random
from typing import Any

from PIL import Image, ImageFilter
from PIL.Image import Resampling

from words_on_paper.background import generate_background
from words_on_paper.composition.animator import (
    calculate_depth_of_field,
    calculate_letter_spacing,
    calculate_scale_factor,
    calculate_text_opacity,
    calculate_visible_chars,
)
from words_on_paper.composition.layer_manager import composite_layers
from words_on_paper.config.schema import TextSequence, VideoConfig
from words_on_paper.rendering.text_renderer import get_text_dimensions, render_text
from words_on_paper.utils.color import hex_to_rgba
from words_on_paper.utils.image import ensure_rgba


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
    background = ensure_rgba(background)

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

    # Determine which text to render (full or visible for typing effect)
    text_to_render = text_seq.content
    if text_seq.effects.typing.enabled and visible_char_count < len(text_seq.content):
        text_to_render = text_seq.content[:visible_char_count]

    # Calculate letter spacing effect
    letter_spacing = 1.0
    center_spacing = False
    if text_seq.effects.letter_spacing.enabled:
        letter_spacing = calculate_letter_spacing(
            current_time=current_time,
            start_time=text_seq.start_time,
            fade_in_duration=text_seq.fade_in_duration,
            display_duration=text_seq.display_duration,
            fade_out_duration=text_seq.fade_out_duration,
            initial_spacing=text_seq.effects.letter_spacing.initial_spacing,
            target_spacing=text_seq.effects.letter_spacing.target_spacing,
            apply_to_fade_out=text_seq.effects.letter_spacing.apply_to_fade_out,
            easing=text_seq.effects.letter_spacing.easing,
        )
        center_spacing = text_seq.effects.letter_spacing.center_spacing

    # Get dimensions of rendered text (for accurate positioning)
    text_width, text_height = get_text_dimensions(
        text_to_render,
        text_seq.font.family,
        text_seq.font.size,
        text_seq.orientation,
        letter_spacing=letter_spacing,
        center_spacing=center_spacing,
    )

    # Render the text
    text_img = render_text(
        text_to_render,
        text_seq.font.family,
        text_seq.font.size,
        text_seq.font.color,
        text_seq.orientation,
        letter_spacing=letter_spacing,
        center_spacing=center_spacing,
    )

    # Calculate and apply scale effect
    scale_factor = 1.0
    if text_seq.effects.scale.enabled:
        scale_factor = calculate_scale_factor(
            current_time=current_time,
            start_time=text_seq.start_time,
            fade_in_duration=text_seq.fade_in_duration,
            display_duration=text_seq.display_duration,
            fade_out_duration=text_seq.fade_out_duration,
            initial_scale=text_seq.effects.scale.initial_scale,
            apply_to_fade_out=text_seq.effects.scale.apply_to_fade_out,
            easing=text_seq.effects.scale.easing,
        )

        if scale_factor != 1.0:
            new_width = int(text_img.width * scale_factor)
            new_height = int(text_img.height * scale_factor)
            # Ensure minimum 1px dimensions
            new_width = max(1, new_width)
            new_height = max(1, new_height)
            text_img = text_img.resize(
                (new_width, new_height),
                Resampling.LANCZOS,
            )
            # Update dimensions to match scaled image
            text_width = text_img.width
            text_height = text_img.height

    # Calculate position based on actual rendered text dimensions
    x, y = calculate_position(
        text_seq.position,
        text_width,
        text_height,
        video_width,
        video_height,
        text_seq.content,
    )

    # Apply opacity
    if opacity < 1.0:
        text_img = _apply_opacity(text_img, opacity)

    # Apply drop shadow if enabled
    if text_seq.effects.drop_shadow.enabled:
        text_img = _apply_drop_shadow(text_img, text_seq.effects.drop_shadow)

    # Apply depth-of-field effect if enabled
    if text_seq.effects.depth_of_field.enabled:
        dof = text_seq.effects.depth_of_field
        distance, blur_radius, dof_alpha = calculate_depth_of_field(
            current_time=current_time,
            start_time=text_seq.start_time,
            inward_frames=dof.inward_frames,
            crisp_frames=dof.crisp_frames,
            outward_frames=dof.outward_frames,
            initial_distance=dof.initial_distance,
            blur_sigma=dof.blur_sigma,
            blur_max_radius=dof.blur_max_radius,
            alpha_sigma=dof.alpha_sigma,
            alpha_min=dof.alpha_min,
        )
        text_img = _apply_depth_of_field_blur(text_img, blur_radius, dof_alpha)

    return text_img, x, y


def _apply_opacity(img: Image.Image, opacity: float) -> Image.Image:
    """Apply opacity to an image."""
    img = ensure_rgba(img)

    # Apply opacity to alpha channel
    alpha = img.split()[3]
    alpha = alpha.point(lambda x: int(x * opacity))

    img.putalpha(alpha)
    return img


def _apply_drop_shadow(img: Image.Image, shadow_config) -> Image.Image:
    """Apply drop shadow effect to an image."""
    img = ensure_rgba(img)

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


def _apply_depth_of_field_blur(
    img: Image.Image, blur_radius: int, alpha_adjust: float
) -> Image.Image:
    """Apply depth-of-field blur and alpha adjustment to an image."""
    img = ensure_rgba(img)

    if blur_radius > 0:
        # Calculate padding based on blur radius
        # Gaussian blur extends significantly, use generous padding to prevent clipping
        padding = max(blur_radius * 6, 20)

        # Create expanded canvas with padding on all sides
        expanded = Image.new(
            "RGBA",
            (img.width + padding * 2, img.height + padding * 2),
            (0, 0, 0, 0),
        )

        # Paste original image centered in expanded canvas
        expanded.paste(img, (padding, padding), img)

        # Apply blur to expanded image (blur extends into padding areas)
        expanded = expanded.filter(ImageFilter.GaussianBlur(blur_radius))

        # Crop back to original size, preserving blur at all edges
        img = expanded.crop(
            (padding, padding, padding + img.width, padding + img.height)
        )

    # Apply alpha adjustment
    if alpha_adjust < 1.0:
        alpha = img.split()[3]
        alpha = alpha.point(lambda x: int(x * alpha_adjust))
        img.putalpha(alpha)

    return img


def calculate_position(
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
