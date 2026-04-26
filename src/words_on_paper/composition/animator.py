"""Animation calculations."""

from __future__ import annotations

import math


def _get_animation_phase(
    current_time: float,
    start_time: float,
    fade_in_duration: float,
    display_duration: float,
    fade_out_duration: float,
) -> tuple[str, float]:
    """
    Determine animation phase and progress within phase.

    Args:
        current_time: Current time in seconds
        start_time: When animation starts
        fade_in_duration: Duration of fade-in phase
        display_duration: Duration of display (full) phase
        fade_out_duration: Duration of fade-out phase

    Returns:
        (phase, progress) tuple where:
        - phase is one of: "before", "fade_in", "display", "fade_out", "after"
        - progress is 0.0-1.0 within the phase (0.0 for before/after)
    """
    if current_time < start_time:
        return "before", 0.0

    fade_in_end = start_time + fade_in_duration
    if current_time < fade_in_end:
        progress = (
            (current_time - start_time) / fade_in_duration
            if fade_in_duration > 0
            else 1.0
        )
        return "fade_in", min(1.0, max(0.0, progress))

    display_end = fade_in_end + display_duration
    if current_time < display_end:
        return "display", 1.0

    fade_out_end = display_end + fade_out_duration
    if current_time < fade_out_end:
        progress = (
            (current_time - display_end) / fade_out_duration
            if fade_out_duration > 0
            else 1.0
        )
        return "fade_out", min(1.0, max(0.0, progress))

    return "after", 0.0


def calculate_text_opacity(
    current_time: float,
    start_time: float,
    fade_in_duration: float,
    display_duration: float,
    fade_out_duration: float,
) -> float:
    """
    Calculate text opacity at a given time.

    Args:
        current_time: Current time in seconds
        start_time: When text starts appearing
        fade_in_duration: Duration of fade in
        display_duration: Duration text is fully opaque
        fade_out_duration: Duration of fade out

    Returns:
        Opacity value from 0.0 to 1.0
    """
    phase, progress = _get_animation_phase(
        current_time, start_time, fade_in_duration, display_duration, fade_out_duration
    )

    if phase == "before":
        return 0.0
    elif phase == "fade_in":
        return progress
    elif phase == "display":
        return 1.0
    elif phase == "fade_out":
        return 1.0 - progress
    else:  # "after"
        return 0.0


def calculate_visible_chars(
    current_time: float,
    start_time: float,
    fade_in_duration: float,
    total_chars: int,
    chars_per_second: float,
) -> int:
    """
    Calculate how many characters are visible for typing effect.

    Args:
        current_time: Current time in seconds
        start_time: When typing starts
        fade_in_duration: Duration of fade in (before typing starts)
        total_chars: Total number of characters
        chars_per_second: Typing speed

    Returns:
        Number of visible characters (0 to total_chars)
    """
    if current_time < start_time:
        return 0

    elapsed = current_time - start_time
    visible = int(elapsed * chars_per_second)

    return min(visible, total_chars)


def _apply_easing(t: float, easing: str) -> float:
    """
    Apply the easing curve to linear progress [0, 1].

    Args:
        t: Linear progress (0.0 to 1.0)
        easing: Easing type

    Returns:
        Eased progress value
    """
    t = max(0.0, min(1.0, t))  # Clamp to [0, 1]

    if easing == "linear":
        return t
    elif easing == "ease_in":
        return t * t
    elif easing == "ease_out":
        return 1.0 - (1.0 - t) ** 2
    elif easing == "ease_in_out":
        if t < 0.5:
            return 2 * t * t
        else:
            return 1.0 - 2 * (1.0 - t) ** 2

    return t  # Fallback to linear


def calculate_scale_factor(
    current_time: float,
    start_time: float,
    fade_in_duration: float,
    display_duration: float,
    fade_out_duration: float,
    initial_scale: float,
    apply_to_fade_out: bool,
    easing: str = "ease_in_out",
) -> float:
    """
    Calculate the scale factor for depth effect during fade animations.

    Args:
        current_time: Current time in seconds
        start_time: When text animation starts
        fade_in_duration: Duration of fade in
        display_duration: Duration at full display
        fade_out_duration: Duration of fade out
        initial_scale: Starting/ending scale (e.g., 0.5 for 50%)
        apply_to_fade_out: If True, shrinks during fade-out
        easing: Easing function type

    Returns:
        Scale factor (initial_scale during fade, 1.0 during display)
    """
    phase, progress = _get_animation_phase(
        current_time, start_time, fade_in_duration, display_duration, fade_out_duration
    )

    if phase == "before" or phase == "after":
        return 1.0
    elif phase == "fade_in":
        eased_progress = _apply_easing(progress, easing)
        return initial_scale + (1.0 - initial_scale) * eased_progress
    elif phase == "display":
        return 1.0
    elif phase == "fade_out":
        if apply_to_fade_out:
            eased_progress = _apply_easing(progress, easing)
            return 1.0 - (1.0 - initial_scale) * eased_progress
        else:
            return 1.0

    return 1.0


def calculate_depth_of_field(
    current_time: float,
    start_time: float,
    inward_frames: int,
    crisp_frames: int,
    outward_frames: int,
    initial_distance: float,
    blur_sigma: float,
    blur_max_radius: int,
    alpha_sigma: float,
    alpha_min: float,
    fps: float = 30.0,
) -> tuple[float, int, float]:
    """
    Calculate depth-of-field effect (blur radius and alpha).

    Args:
        current_time: Current time in seconds
        start_time: When animation starts
        inward_frames: Frames for approach phase
        crisp_frames: Frames at focus
        outward_frames: Frames for recession phase
        initial_distance: Starting distance from focal plane (0.0-1.0)
        blur_sigma: Gaussian sigma for blur
        blur_max_radius: Maximum blur radius in pixels
        alpha_sigma: Gaussian sigma for alpha
        alpha_min: Minimum alpha when out of focus
        fps: Frames per second (for time->frame conversion)

    Returns:
        (distance, blur_radius, alpha) tuple
    """
    inward_duration = inward_frames / fps
    crisp_duration = crisp_frames / fps
    outward_duration = outward_frames / fps
    total_duration = inward_duration + crisp_duration + outward_duration

    elapsed = current_time - start_time

    # Before animation starts
    if elapsed < 0:
        return initial_distance, 0, alpha_min

    # After animation ends
    if elapsed >= total_duration:
        return 1.0, 0, alpha_min

    # Determine phase and calculate distance
    if elapsed < inward_duration:
        # Inward phase: distance goes from initial_distance to ~0
        progress = elapsed / inward_duration
        distance = initial_distance * (1.0 - progress)
    elif elapsed < inward_duration + crisp_duration:
        # Crisp phase: stay near focus
        distance = 0.05
    else:
        # Outward phase: distance goes from ~0 to 1.0
        outward_progress = (
            elapsed - inward_duration - crisp_duration
        ) / outward_duration
        distance = outward_progress

    # Calculate blur and alpha from Gaussian curves centered at focal plane (distance=0)
    # At distance d, Gaussian = exp(-(d^2) / (2*sigma^2))
    blur_gaussian = math.exp(-((distance**2) / (2 * blur_sigma**2)))
    alpha_gaussian = math.exp(-((distance**2) / (2 * alpha_sigma**2)))

    # Map Gaussian values to blur radius and alpha
    blur_radius = int(blur_gaussian * blur_max_radius)
    alpha = alpha_min + (1.0 - alpha_min) * alpha_gaussian

    return distance, blur_radius, alpha
