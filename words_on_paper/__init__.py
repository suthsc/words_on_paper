"""Words on Paper - Video generator creating animated text on paper-like backgrounds."""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from words_on_paper.config import VideoConfig, load_config
from words_on_paper.video import generate_video

__all__ = ["load_config", "VideoConfig", "generate_video"]
