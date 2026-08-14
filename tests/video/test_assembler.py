"""Tests for video assembly (video/assembler.py)."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path

import numpy as np
import pytest

from words_on_paper.composition.frame_builder import build_frame
from words_on_paper.config.schema import BackgroundConfig, TextSequence, VideoConfig
from words_on_paper.video import assembler


def _tiny_config(duration: float = 1.0, fps: int = 10, size: int = 32) -> VideoConfig:
    """A minimal, fast-to-render config for tests.

    Uses a solid background (no random noise) so frames built in different
    processes are byte-for-byte comparable in tests.
    """
    return VideoConfig(
        video={"width": size, "height": size, "fps": fps},
        background=BackgroundConfig(type="solid"),
        texts=[
            TextSequence(
                content="Hi",
                start_time=0.0,
                fade_in_duration=0.0,
                display_duration=duration,
                fade_out_duration=0.0,
            )
        ],
    )


class _FakeFuture:
    """A Future stand-in whose result() is available immediately, but reports
    back to the owning executor when consumed so tests can observe how many
    submissions were outstanding (submitted but not yet awaited) at once."""

    def __init__(self, value: object, on_result: Callable[[], None]) -> None:
        self._value = value
        self._on_result = on_result

    def result(self) -> object:
        self._on_result()
        return self._value


class _RecordingExecutor:
    """Test double for ProcessPoolExecutor that runs submissions inline but
    tracks the number of outstanding (submitted, not-yet-awaited) futures,
    to verify the bounded-window submission discipline in _stream_frames."""

    instances: list["_RecordingExecutor"] = []

    def __init__(self, max_workers: int | None = None) -> None:
        self.max_workers = max_workers
        self.outstanding = 0
        self.max_outstanding = 0
        self.submitted_batches: list[list[int]] = []
        _RecordingExecutor.instances.append(self)

    def submit(
        self, fn: object, config: VideoConfig, batch: list[int], fps: int
    ) -> _FakeFuture:
        self.submitted_batches.append(batch)
        self.outstanding += 1
        self.max_outstanding = max(self.max_outstanding, self.outstanding)
        assert callable(fn)
        value = fn(config, batch, fps)

        def on_result() -> None:
            self.outstanding -= 1

        return _FakeFuture(value, on_result)

    def __enter__(self) -> "_RecordingExecutor":
        return self

    def __exit__(self, *exc_info: object) -> None:
        return None


class TestStreamFrames:
    """Test the bounded-window frame streaming generator."""

    def test_yields_frames_in_order_matching_build_frame(self) -> None:
        config = _tiny_config(duration=0.5, fps=10)
        total_frames = 5
        frames = list(
            assembler._stream_frames(
                config, total_frames, fps=10, chunk_size=2, max_workers=2
            )
        )

        assert len(frames) == total_frames
        for i, frame in enumerate(frames):
            expected = np.array(build_frame(config, i / 10))
            assert np.array_equal(frame, expected)

    def test_bounds_in_flight_batches_to_max_workers(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _RecordingExecutor.instances.clear()
        monkeypatch.setattr(assembler, "ProcessPoolExecutor", _RecordingExecutor)

        config = _tiny_config(duration=1.0, fps=10)
        total_frames = 10
        max_workers = 3
        frames = list(
            assembler._stream_frames(
                config, total_frames, fps=10, chunk_size=1, max_workers=max_workers
            )
        )

        assert len(frames) == total_frames
        executor = _RecordingExecutor.instances[-1]
        # 10 batches > max_workers, so the window should have filled up
        # completely at some point, but never exceeded it.
        assert executor.max_outstanding == max_workers
        assert len(executor.submitted_batches) == total_frames  # chunk_size=1


class TestSequentialFrameFeeder:
    """Test the make_frame(t) adapter over a pull-based frame iterator."""

    def test_advances_forward_in_lockstep_with_index(self) -> None:
        frames = [np.array([i]) for i in range(5)]
        feeder = assembler._SequentialFrameFeeder(iter(frames), fps=10)

        for i in range(5):
            result = feeder(i / 10)
            assert np.array_equal(result, frames[i])

    def test_does_not_advance_within_the_same_frame_interval(self) -> None:
        frames = [np.array([0]), np.array([1])]
        feeder = assembler._SequentialFrameFeeder(iter(frames), fps=10)

        first = feeder(0.0)
        # 0.04s still rounds to frame index 0 at fps=10
        same = feeder(0.04)

        assert np.array_equal(first, same)
        assert np.array_equal(same, frames[0])


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg not available")
class TestGenerateVideo:
    """End-to-end test of generate_video using the streaming pipeline."""

    def test_generate_video_writes_expected_frame_count(self, tmp_path: Path) -> None:
        config = _tiny_config(duration=0.3, fps=10, size=32)
        output_path = tmp_path / "out.mp4"

        assembler.generate_video(config, output_path)

        assert output_path.exists()
        assert output_path.stat().st_size > 0
