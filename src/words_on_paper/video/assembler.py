"""Video assembly using MoviePy."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from tqdm import tqdm

from words_on_paper.composition.frame_builder import build_frame
from words_on_paper.config.schema import VideoConfig
from words_on_paper.utils.timing import calculate_frame_count


def _generate_frame_batch(
    config: VideoConfig, frame_numbers: list[int], fps: int
) -> tuple[int, list[np.ndarray]]:
    """
    Generate a batch of frames.

    Args:
        config: Video configuration
        frame_numbers: List of frame numbers to generate
        fps: Frames per second

    Returns:
        Tuple of (batch_start_index, list of frame arrays)
    """
    frames = []
    batch_start = frame_numbers[0]
    batch_end = frame_numbers[-1]
    start_time = batch_start / fps

    pbar = tqdm(
        frame_numbers,
        desc=f"Chunk [{int(start_time // 60):02d}:{int(start_time % 60):02d} - {int(batch_end / fps // 60):02d}:{int(batch_end / fps % 60):02d}]",
        leave=False,
    )
    for frame_num in pbar:
        time = frame_num / fps
        frame = build_frame(config, time)
        frames.append(np.array(frame))

    return batch_start, frames


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

    # Generate frames in parallel batches
    chunk_size = 100  # Process ~100 frames per worker task
    num_chunks = (total_frames + chunk_size - 1) // chunk_size

    # Create list of frame batches
    batches = [
        list(range(i * chunk_size, min((i + 1) * chunk_size, total_frames)))
        for i in range(num_chunks)
    ]

    # Submit all batch jobs and collect results in order
    frames_dict: dict[int, list[np.ndarray]] = {}
    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(_generate_frame_batch, config, batch, int(fps)): batch
            for batch in batches
        }

        with tqdm(total=num_chunks, desc="Processing chunks", unit="chunk") as pbar:
            for future in as_completed(futures):
                start_frame_num, frame_batch = future.result()
                frames_dict[start_frame_num] = frame_batch
                # Update progress
                pbar.update(1)
                # Show chunks completed and time progress
                total_frames_done = sum(len(batch) for batch in frames_dict.values())
                time_done = total_frames_done / fps
                mins, secs = divmod(time_done, 60)
                pbar.set_postfix(
                    {
                        "frames": f"{total_frames_done}/{total_frames}",
                        "time": f"{int(mins):02d}:{secs:05.2f}",
                    }
                )

    # Reconstruct frames in correct order
    frames = []
    for frame_num in range(total_frames):
        batch_start = (frame_num // chunk_size) * chunk_size
        batch_offset = frame_num % chunk_size
        frames.append(frames_dict[batch_start][batch_offset])

    # Create video clip
    clip = ImageSequenceClip(frames, fps=fps)

    # Write video file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    clip.write_videofile(str(output_path))
