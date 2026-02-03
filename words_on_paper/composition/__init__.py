"""Frame composition and animation."""

from words_on_paper.composition.animator import (
    calculate_scale_factor,
    calculate_text_opacity,
    calculate_visible_chars,
)
from words_on_paper.composition.frame_builder import build_frame
from words_on_paper.composition.layer_manager import composite_layers

__all__ = [
    "build_frame",
    "composite_layers",
    "calculate_text_opacity",
    "calculate_visible_chars",
    "calculate_scale_factor",
]
