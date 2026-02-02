"""Configuration loading and parsing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from words_on_paper.config.schema import VideoConfig


def load_config(config_path: str | Path) -> VideoConfig:
    """
    Load and validate configuration from JSON or YAML file.

    Args:
        config_path: Path to configuration file (.json or .yaml/.yml)

    Returns:
        Validated VideoConfig object

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config format is invalid or validation fails
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    suffix = config_path.suffix.lower()

    if suffix == ".json":
        data = _load_json(config_path)
    elif suffix in (".yaml", ".yml"):
        data = _load_yaml(config_path)
    else:
        raise ValueError(f"Unsupported config format: {suffix}")

    return VideoConfig(**data)


def _load_json(path: Path) -> dict[str, Any]:
    """Load JSON configuration file."""
    try:
        with open(path) as f:
            return json.load(f)  # type: ignore
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}") from e


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load YAML configuration file."""
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
            if data is None:
                return {}
            if not isinstance(data, dict):
                raise ValueError("Configuration must be a YAML/JSON object")
            return data
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {path}: {e}") from e
