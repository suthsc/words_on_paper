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
    # Typing starts after fade in
    typing_start = start_time + fade_in_duration

    if current_time < typing_start:
        return 0

    elapsed = current_time - typing_start
    visible = int(elapsed * chars_per_second)

    return min(visible, total_chars)
