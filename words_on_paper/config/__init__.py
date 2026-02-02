"""Configuration management for Words on Paper."""

from words_on_paper.config.loader import load_config
from words_on_paper.config.schema import VideoConfig

__all__ = ["load_config", "VideoConfig"]
