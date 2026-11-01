"""Pydantic models for configuration validation."""

from __future__ import annotations

from typing import Any, Literal, Optional, Union

from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)

from words_on_paper.config.styles import EXTENDS_KEY, STYLE_KEY, resolve_config


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


class DepthOfFieldEffect(BaseModel):
    """Depth-of-field focal plane effect."""

    enabled: bool = False
    initial_distance: float = Field(default=0.5, ge=0.0, le=1.0)
    inward_frames: int = Field(default=30, ge=0)
    crisp_frames: int = Field(default=60, ge=0)
    outward_frames: int = Field(default=30, ge=0)
    blur_sigma: float = Field(default=0.2, gt=0.0, le=1.0)
    blur_max_radius: int = Field(default=25, ge=0)
    alpha_sigma: float = Field(default=0.2, gt=0.0, le=1.0)
    alpha_min: float = Field(default=0.3, ge=0.0, lt=1.0)


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


class ScaleEffect(BaseModel):
    """Scale/depth effect during fade animations."""

    enabled: bool = False
    initial_scale: float = Field(default=0.5, gt=0.0, le=1.0)
    apply_to_fade_out: bool = True
    easing: Literal["linear", "ease_in", "ease_out", "ease_in_out"] = "ease_in_out"


class LetterSpacingEffect(BaseModel):
    """Letter spacing effect to create perspective/distance illusion.

    Two spacing modes:
    - Sequential (center_spacing=False): Characters spaced uniformly from start to end
    - Centered (center_spacing=True): Spacing varies symmetrically around text center
      (tighter in center, wider at edges)

    Spacing values are automatically clamped to MIN_READABLE_SPACING (0.75) to maintain
    text readability. Recommended ranges:
    - Sequential: target_spacing >= 0.75 (0.75-1.5 recommended)
    - Centered: target_spacing >= 0.75 (0.80-1.0 recommended, as edge spacing remains wide)
    """

    enabled: bool = False
    initial_spacing: float = Field(
        default=1.0, gt=0.0, description="Starting spacing multiplier"
    )
    target_spacing: float = Field(
        default=0.7, gt=0.0, description="Target spacing (auto-clamped to 0.75 minimum)"
    )
    apply_to_fade_out: bool = True
    center_spacing: bool = False
    easing: Literal["linear", "ease_in", "ease_out", "ease_in_out"] = "ease_in_out"


class Effects(BaseModel):
    """Effect configurations."""

    typing: TypingEffect = Field(default_factory=TypingEffect)
    drop_shadow: DropShadow = Field(default_factory=DropShadow)
    scale: ScaleEffect = Field(default_factory=ScaleEffect)
    letter_spacing: LetterSpacingEffect = Field(default_factory=LetterSpacingEffect)
    depth_of_field: DepthOfFieldEffect = Field(default_factory=DepthOfFieldEffect)


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
    style: Optional[Union[str, list[str]]] = Field(
        default=None,
        description="Name(s) of styles applied before inline fields (later wins)",
    )


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
    defaults: dict[str, Any] = Field(
        default_factory=dict,
        description="TextSequence fields applied to every text (lowest precedence)",
    )
    styles: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Named, reusable TextSequence fragments; may 'extends' others",
    )
    texts: list[TextSequence] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def apply_styles(cls, data: Any) -> Any:
        """Check style fragments, then expand defaults/styles into each text."""
        if not isinstance(data, dict):
            return data
        defaults = data.get("defaults")
        styles = data.get("styles")
        if isinstance(defaults, dict):
            _check_fragment(defaults, TextSequence, "defaults", forbid={STYLE_KEY})
        if isinstance(styles, dict):
            for name, body in styles.items():
                if isinstance(body, dict):
                    _check_fragment(
                        body,
                        TextSequence,
                        f"styles.{name}",
                        allow={EXTENDS_KEY},
                        forbid={STYLE_KEY},
                    )
        resolved = resolve_config(data)
        _explain_styled_text_errors(resolved)
        return resolved

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


def _check_fragment(
    fragment: dict[str, Any],
    model: type[BaseModel],
    path: str,
    allow: frozenset[str] | set[str] = frozenset(),
    forbid: frozenset[str] | set[str] = frozenset(),
) -> None:
    """Raise ValueError for keys in ``fragment`` that ``model`` doesn't define.

    Pydantic ignores unknown keys, which would make a typo in a style (say
    ``colour``) silently drop the setting for every text using it. Nested
    model fields (font, position, effects.*) are checked recursively.
    """
    for key, value in fragment.items():
        if key in allow:
            continue
        if key in forbid:
            raise ValueError(f"{path}.{key}: not allowed here")
        field = model.model_fields.get(key)
        if field is None:
            raise ValueError(f"{path}.{key}: unknown field")
        sub = field.annotation
        if (
            isinstance(sub, type)
            and issubclass(sub, BaseModel)
            and isinstance(value, dict)
        ):
            _check_fragment(value, sub, f"{path}.{key}")


def _explain_styled_text_errors(resolved: Any) -> None:
    """Re-raise validation errors in styled texts with their index and styles.

    After the cascade, a bad value may come from a style rather than the text
    itself, so name the styles involved. Unstyled texts are left for the normal
    Pydantic error.
    """
    if not isinstance(resolved, dict) or not isinstance(resolved.get("texts"), list):
        return
    for i, text in enumerate(resolved["texts"]):
        if not isinstance(text, dict) or text.get(STYLE_KEY) is None:
            continue
        try:
            TextSequence.model_validate(text)
        except ValidationError as exc:
            style = text[STYLE_KEY]
            names = ", ".join(style) if isinstance(style, list) else style
            problems = "; ".join(
                f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}"
                for err in exc.errors()
            )
            raise ValueError(f"texts[{i}] (style: {names}): {problems}") from None
