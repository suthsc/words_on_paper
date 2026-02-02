"""Pydantic models for configuration validation."""

from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator


class Position(BaseModel):
    """Text positioning configuration."""

    mode: Literal["center", "absolute", "relative", "random"] = "center"
    x: Optional[float] = None
    y: Optional[float] = None

    @field_validator("x", "y")
    @classmethod
    def validate_coordinates(cls, v: Optional[float], info) -> Optional[float]:
        """Validate coordinate values."""
        if v is not None and v < 0:
            raise ValueError("Coordinates must be non-negative")
        return v


class Font(BaseModel):
    """Font configuration for text rendering."""

    family: str = "Arial"
    size: int = Field(default=72, gt=0, description="Font size in pixels")
    color: str = "#000000"


class TypingEffect(BaseModel):
    """Configuration for typing/reveal effect."""

    enabled: bool = False
    chars_per_second: float = Field(default=10.0, gt=0)


class DropShadow(BaseModel):
    """Configuration for drop shadow effect."""

    enabled: bool = True
    offset_x: int = 2
    offset_y: int = 2
    blur_radius: int = 3
    color: str = "#00000040"


class Effects(BaseModel):
    """Effect configurations."""

    typing: TypingEffect = Field(default_factory=TypingEffect)
    drop_shadow: DropShadow = Field(default_factory=DropShadow)


class TextSequence(BaseModel):
    """Configuration for a single text sequence/animation."""

    content: str
    start_time: float = Field(default=0.0, ge=0)
    fade_in_duration: float = Field(default=1.0, ge=0)
    display_duration: float = Field(default=3.0, ge=0)
    fade_out_duration: float = Field(default=1.0, ge=0)
    orientation: Literal["horizontal", "vertical"] = "horizontal"
    position: Position = Field(default_factory=Position)
    font: Font = Field(default_factory=Font)
    effects: Effects = Field(default_factory=Effects)
    z_index: int = 0


class BackgroundConfig(BaseModel):
    """Background configuration."""

    type: Literal["paper", "solid"] = "paper"
    color: str = "#FFFFFF"
    texture_intensity: float = Field(default=0.05, ge=0.0, le=1.0)


class VideoConfig(BaseModel):
    """Root configuration for video generation."""

    video: dict[str, Any] = Field(
        default_factory=lambda: {
            "width": 1920,
            "height": 1080,
            "fps": 30,
        }
    )
    background: BackgroundConfig = Field(default_factory=BackgroundConfig)
    texts: list[TextSequence] = Field(default_factory=list)

    @field_validator("video")
    @classmethod
    def validate_video_config(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Validate video configuration."""
        width = v.get("width", 1920)
        height = v.get("height", 1080)
        fps = v.get("fps", 30)

        if not isinstance(width, int) or width <= 0:
            raise ValueError("Video width must be a positive integer")
        if not isinstance(height, int) or height <= 0:
            raise ValueError("Video height must be a positive integer")
        if not isinstance(fps, int) or fps <= 0:
            raise ValueError("Video fps must be a positive integer")

        return v

    def get_video_duration(self) -> float:
        """Calculate total video duration in seconds."""
        if not self.texts:
            return 0.0

        max_end_time = 0.0
        for text in self.texts:
            end_time = (
                text.start_time
                + text.fade_in_duration
                + text.display_duration
                + text.fade_out_duration
            )
            max_end_time = max(max_end_time, end_time)

        return max_end_time
