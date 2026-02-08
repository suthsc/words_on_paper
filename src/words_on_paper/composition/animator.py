"""Animation calculations."""


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
    # Before start time
    if current_time < start_time:
        return 0.0

    # Fade in phase
    fade_in_end = start_time + fade_in_duration
    if current_time < fade_in_end:
        progress = (current_time - start_time) / fade_in_duration
        return min(1.0, max(0.0, progress))

    # Display phase
    display_end = fade_in_end + display_duration
    if current_time < display_end:
        return 1.0

    # Fade out phase
    fade_out_end = display_end + fade_out_duration
    if current_time < fade_out_end:
        progress = (current_time - display_end) / fade_out_duration
        return max(0.0, 1.0 - progress)

    # After fade out
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
    fade_in_end = start_time + fade_in_duration
    fade_out_start = fade_in_end + display_duration
    fade_out_end = fade_out_start + fade_out_duration

    # Before animation or after animation
    if current_time < start_time or current_time >= fade_out_end:
        return 1.0

    # Fade-in phase: scale from initial_scale to 1.0
    if current_time < fade_in_end:
        progress = (current_time - start_time) / fade_in_duration
        progress = _apply_easing(progress, easing)
        return initial_scale + (1.0 - initial_scale) * progress

    # Display phase: full scale
    if current_time < fade_out_start:
        return 1.0

    # Fade-out phase: scale from 1.0 to initial_scale (if enabled)
    if apply_to_fade_out:
        progress = (current_time - fade_out_start) / fade_out_duration
        progress = _apply_easing(progress, easing)
        return 1.0 - (1.0 - initial_scale) * progress

    return 1.0
