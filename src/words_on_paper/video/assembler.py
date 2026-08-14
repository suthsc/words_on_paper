"""Video assembly using MoviePy."""

from __future__ import annotations

from collections import deque
from collections.abc import Generator, Iterator
from concurrent.futures import Future, ProcessPoolExecutor
from pathlib import Path

import numpy as np
from moviepy.video.VideoClip import VideoClip
from tqdm import tqdm

from words_on_paper.composition.frame_builder import build_frame
from words_on_paper.config.schema import VideoConfig
from words_on_paper.utils.timing import calculate_frame_count

CHUNK_SIZE = 100  # Frames generated per worker task
MAX_WORKERS = 8


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


def _stream_frames(
    config: VideoConfig,
    total_frames: int,
    fps: int,
    chunk_size: int = CHUNK_SIZE,
    max_workers: int = MAX_WORKERS,
    progress: tqdm | None = None,
) -> Generator[np.ndarray, None, None]:
    """
    Yield video frames in order using a bounded-ahead worker pool.

    At most `max_workers` chunks are ever in flight at once (submitted but
    not yet consumed), so peak resident frame count stays roughly constant
    at ~max_workers * chunk_size regardless of total video length, instead
    of the whole video's frames being materialized at once.
    """
    batches = [
        list(range(start, min(start + chunk_size, total_frames)))
        for start in range(0, total_frames, chunk_size)
    ]

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        pending: deque[Future[tuple[int, list[np.ndarray]]]] = deque()
        next_batch_idx = 0

        def submit_next() -> None:
            nonlocal next_batch_idx
            if next_batch_idx < len(batches):
                pending.append(
                    executor.submit(
                        _generate_frame_batch, config, batches[next_batch_idx], fps
                    )
                )
                next_batch_idx += 1

        for _ in range(min(max_workers, len(batches))):
            submit_next()

        frames_done = 0
        while pending:
            _, frame_batch = pending.popleft().result()
            submit_next()

            frames_done += len(frame_batch)
            if progress is not None:
                progress.update(1)
                time_done = frames_done / fps
                mins, secs = divmod(time_done, 60)
                progress.set_postfix(
                    {
                        "frames": f"{frames_done}/{total_frames}",
                        "time": f"{int(mins):02d}:{secs:05.2f}",
                    }
                )

            yield from frame_batch


class _SequentialFrameFeeder:
    """
    Adapts a pull-based, in-order frame iterator to MoviePy's make_frame(t).

    Relies on MoviePy calling make_frame with a strictly non-decreasing t
    during write_videofile (verified against moviepy 1.0.3's
    Clip.iter_frames), so frames can be advanced forward-only without
    buffering frames the caller has already moved past.
    """

    def __init__(self, frames: Iterator[np.ndarray], fps: float) -> None:
        self._frames = frames
        self._fps = fps
        self._next_index = 0
        self._current: np.ndarray | None = None

    def __call__(self, t: float) -> np.ndarray:
        index = round(t * self._fps)
        while self._next_index <= index:
            self._current = next(self._frames)
            self._next_index += 1
        assert self._current is not None
        return self._current


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

    total_frames = calculate_frame_count(duration, int(fps))
    num_chunks = (total_frames + CHUNK_SIZE - 1) // CHUNK_SIZE

    with tqdm(total=num_chunks, desc="Processing chunks", unit="chunk") as pbar:
        frame_stream = _stream_frames(config, total_frames, int(fps), progress=pbar)
        try:
            feeder = _SequentialFrameFeeder(frame_stream, fps)
            # Match VideoClip's frame count exactly to total_frames so
            # write_videofile's iter_frames() pulls precisely as many
            # frames as the stream produces.
            clip = VideoClip(make_frame=feeder, duration=total_frames / fps)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            clip.write_videofile(str(output_path), fps=fps)
        finally:
            frame_stream.close()
