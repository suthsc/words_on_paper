"""Timing utilities for frame/time conversions."""


def frame_to_time(frame_number: int, fps: int) -> float:
    """
    Convert frame number to time in seconds.

    Args:
        frame_number: Frame number (0-indexed)
        fps: Frames per second

    Returns:
        Time in seconds
    """
    if fps <= 0:
        raise ValueError("FPS must be positive")
    return frame_number / fps


def time_to_frame(time_seconds: float, fps: int) -> int:
    """
    Convert time in seconds to frame number.

    Args:
        time_seconds: Time in seconds
        fps: Frames per second

    Returns:
        Frame number (0-indexed)
    """
    if fps <= 0:
        raise ValueError("FPS must be positive")
    return int(time_seconds * fps)


def calculate_frame_count(duration_seconds: float, fps: int) -> int:
    """
    Calculate total frame count for a video duration.

    Args:
        duration_seconds: Video duration in seconds
        fps: Frames per second

    Returns:
        Total frame count
    """
    if fps <= 0:
        raise ValueError("FPS must be positive")
    return int(duration_seconds * fps)
