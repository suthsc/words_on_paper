"""Tests for configuration loading."""

import json
import tempfile
from pathlib import Path

import pytest
import yaml

from words_on_paper.config.loader import load_config
from words_on_paper.config.schema import VideoConfig


class TestLoadConfig:
    """Test configuration loading."""

    def test_load_json_config(self) -> None:
        """Test loading JSON configuration."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config_data = {
                "video": {"width": 1920, "height": 1080, "fps": 30},
                "background": {"type": "paper", "color": "#FFFFFF"},
                "texts": [
                    {
                        "content": "Hello",
                        "start_time": 0.0,
                        "fade_in_duration": 1.0,
                    }
                ],
            }
            json.dump(config_data, f)
            f.flush()

            config = load_config(f.name)
            assert isinstance(config, VideoConfig)
            assert config.video["width"] == 1920
            assert len(config.texts) == 1
            assert config.texts[0].content == "Hello"

            Path(f.name).unlink()

    def test_load_yaml_config(self) -> None:
        """Test loading YAML configuration."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            config_data = {
                "video": {"width": 1920, "height": 1080, "fps": 30},
                "background": {"type": "paper"},
                "texts": [
                    {
                        "content": "Test",
                        "start_time": 1.0,
                        "fade_in_duration": 0.5,
                    }
                ],
            }
            yaml.dump(config_data, f)
            f.flush()

            config = load_config(f.name)
            assert isinstance(config, VideoConfig)
            assert config.texts[0].content == "Test"

            Path(f.name).unlink()

    def test_load_yml_config(self) -> None:
        """Test loading YML configuration."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            config_data = {"video": {"width": 1280, "height": 720, "fps": 24}}
            yaml.dump(config_data, f)
            f.flush()

            config = load_config(f.name)
            assert config.video["width"] == 1280
            assert config.video["height"] == 720

            Path(f.name).unlink()

    def test_load_missing_file(self) -> None:
        """Test loading non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent.yaml")

    def test_load_invalid_json(self) -> None:
        """Test loading invalid JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{invalid json}")
            f.flush()

            with pytest.raises(ValueError, match="Invalid JSON"):
                load_config(f.name)

            Path(f.name).unlink()

    def test_load_invalid_yaml(self) -> None:
        """Test loading invalid YAML."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: [yaml: content")
            f.flush()

            with pytest.raises(ValueError, match="Invalid YAML"):
                load_config(f.name)

            Path(f.name).unlink()

    def test_load_unsupported_format(self) -> None:
        """Test loading unsupported format."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test")
            f.flush()

            with pytest.raises(ValueError, match="Unsupported config format"):
                load_config(f.name)

            Path(f.name).unlink()

    def test_load_empty_yaml(self) -> None:
        """Test loading empty YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            f.flush()

            config = load_config(f.name)
            assert isinstance(config, VideoConfig)

            Path(f.name).unlink()

    def test_load_path_object(self) -> None:
        """Test loading with Path object."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"video": {"width": 1920, "height": 1080, "fps": 30}}, f)
            f.flush()

            config = load_config(Path(f.name))
            assert isinstance(config, VideoConfig)

            Path(f.name).unlink()
