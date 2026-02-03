"""Video assembly using MoviePy."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from tqdm import tqdm

from words_on_paper.composition.frame_builder import build_frame
from words_on_paper.config.schema import VideoConfig
from words_on_paper.utils.timing import calculate_frame_count


def generate_video(config: VideoConfig, output_path: str | Path) -> None:
    """
    Generate a video from configuration.

    Args:
        config: Video configuration
        output_path: Path to save output video file

    Raises:
        ValueError: If config or output path is invalid
    """
    output_path = Path(output_path)

    # Validate config
    duration = config.get_video_duration()
    if duration == 0:
        raise ValueError("No video duration configured (no text sequences)")

    width = config.video["width"]
    height = config.video["height"]
    fps = config.video["fps"]

    if width <= 0 or height <= 0:
        raise ValueError("Invalid video resolution")
    if fps <= 0:
        raise ValueError("Invalid fps")

    # Calculate total frames
    total_frames = calculate_frame_count(duration, int(fps))

    # Generate frames
    frames = []
    pbar = tqdm(
        range(total_frames),
        desc="Generating frames",
        total=total_frames,
    )
    for frame_num in pbar:
        time = frame_num / fps
        frame = build_frame(config, time)
        frames.append(np.array(frame))
        # Update progress bar to show current time
        mins, secs = divmod(time, 60)
        pbar.set_description(f"Generating frames (time: {int(mins):02d}:{secs:05.2f})")

    # Create video clip
    clip = ImageSequenceClip(frames, fps=fps)

    # Write video file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    clip.write_videofile(str(output_path))
