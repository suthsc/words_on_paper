"""Tests for timing utilities."""

import pytest

from words_on_paper.utils.timing import (
    calculate_frame_count,
    frame_to_time,
    time_to_frame,
)


class TestFrameToTime:
    """Test frame to time conversion."""

    def test_frame_to_time_zero(self) -> None:
        """Test frame 0 converts to 0 seconds."""
        assert frame_to_time(0, 30) == 0.0

    def test_frame_to_time_standard(self) -> None:
        """Test standard frame to time conversion."""
        assert frame_to_time(30, 30) == 1.0
        assert frame_to_time(60, 30) == 2.0

    def test_frame_to_time_24fps(self) -> None:
        """Test with 24 fps."""
        assert frame_to_time(24, 24) == 1.0

    def test_frame_to_time_60fps(self) -> None:
        """Test with 60 fps."""
        assert frame_to_time(60, 60) == 1.0

    def test_frame_to_time_invalid_fps(self) -> None:
        """Test invalid fps."""
        with pytest.raises(ValueError):
            frame_to_time(30, 0)


class TestTimeToFrame:
    """Test time to frame conversion."""

    def test_time_to_frame_zero(self) -> None:
        """Test 0 seconds converts to frame 0."""
        assert time_to_frame(0.0, 30) == 0

    def test_time_to_frame_standard(self) -> None:
        """Test standard time to frame conversion."""
        assert time_to_frame(1.0, 30) == 30
        assert time_to_frame(2.0, 30) == 60

    def test_time_to_frame_fractional(self) -> None:
        """Test fractional seconds."""
        assert time_to_frame(0.5, 30) == 15

    def test_time_to_frame_24fps(self) -> None:
        """Test with 24 fps."""
        assert time_to_frame(1.0, 24) == 24

    def test_time_to_frame_rounding(self) -> None:
        """Test that fractional frames are rounded down."""
        assert time_to_frame(1.1, 30) == 33

    def test_time_to_frame_invalid_fps(self) -> None:
        """Test invalid fps."""
        with pytest.raises(ValueError):
            time_to_frame(1.0, 0)


class TestCalculateFrameCount:
    """Test frame count calculation."""

    def test_calculate_frame_count_standard(self) -> None:
        """Test standard frame count calculation."""
        assert calculate_frame_count(10.0, 30) == 300

    def test_calculate_frame_count_zero_duration(self) -> None:
        """Test zero duration."""
        assert calculate_frame_count(0.0, 30) == 0

    def test_calculate_frame_count_24fps(self) -> None:
        """Test with 24 fps."""
        assert calculate_frame_count(1.0, 24) == 24

    def test_calculate_frame_count_60fps(self) -> None:
        """Test with 60 fps."""
        assert calculate_frame_count(5.0, 60) == 300

    def test_calculate_frame_count_invalid_fps(self) -> None:
        """Test invalid fps."""
        with pytest.raises(ValueError):
            calculate_frame_count(10.0, 0)
