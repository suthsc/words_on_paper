"""Tests for the Click CLI."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from words_on_paper.cli import cli

STYLED = """
defaults:
  font: {family: Courier, size: 40}
styles:
  base: {z_index: 7}
  vlad:
    extends: base
    font: {color: "#1A5490"}
texts:
  - content: hello
    style: vlad
    font: {size: 50}
  - content: plain
"""


@pytest.fixture
def styled_config(tmp_path: Path) -> Path:
    """A small config that uses defaults, styles and extends."""
    path = tmp_path / "styled.yaml"
    path.write_text(STYLED)
    return path


def _parse_resolved(output: str) -> list[dict]:
    """Collect the YAML list items printed by --resolved."""
    yaml_lines = [ln for ln in output.splitlines() if ln.startswith(("-", " "))]
    parsed: list[dict] = yaml.safe_load("\n".join(yaml_lines))
    return parsed


def test_validate_plain(styled_config: Path) -> None:
    """validate without flags prints the summary only."""
    result = CliRunner().invoke(cli, ["validate", str(styled_config)])
    assert result.exit_code == 0, result.output
    assert "Configuration is valid" in result.output
    assert "texts[0]" not in result.output


def test_validate_resolved_shows_merged_values(styled_config: Path) -> None:
    """--resolved prints every text with the cascade applied."""
    result = CliRunner().invoke(cli, ["validate", str(styled_config), "--resolved"])
    assert result.exit_code == 0, result.output
    assert "# texts[0]" in result.output and "# texts[1]" in result.output
    first, second = _parse_resolved(result.output)
    assert list(first)[0] == "style"
    assert first["style"] == "vlad"
    assert first["font"] == {"family": "Courier", "size": 50, "color": "#1A5490"}
    assert first["z_index"] == 7
    assert "style" not in second
    assert second["font"]["family"] == "Courier"
    assert second["z_index"] == 0


def test_validate_text_index(styled_config: Path) -> None:
    """--text N prints only that text (and implies --resolved)."""
    result = CliRunner().invoke(cli, ["validate", str(styled_config), "--text", "1"])
    assert result.exit_code == 0, result.output
    assert "# texts[1]" in result.output
    assert "# texts[0]" not in result.output
    (only,) = _parse_resolved(result.output)
    assert only["content"] == "plain"


def test_validate_text_index_out_of_range(styled_config: Path) -> None:
    """An out-of-range --text index is a clean error."""
    result = CliRunner().invoke(cli, ["validate", str(styled_config), "--text", "5"])
    assert result.exit_code == 1
    assert "out of range" in result.output


def test_validate_error_exits_cleanly(tmp_path: Path) -> None:
    """A bad config prints an error and exits 1 (no traceback)."""
    path = tmp_path / "bad.yaml"
    path.write_text("texts:\n  - content: a\n    style: nope\n")
    result = CliRunner().invoke(cli, ["validate", str(path)])
    assert result.exit_code == 1
    assert "unknown style 'nope'" in result.output
    assert not isinstance(result.exception, AttributeError)


def test_generate_error_exits_cleanly(tmp_path: Path) -> None:
    """generate reports config errors cleanly too."""
    path = tmp_path / "bad.yaml"
    path.write_text("styles:\n  a: {font: {colour: red}}\n")
    out = tmp_path / "out.mp4"
    result = CliRunner().invoke(cli, ["generate", str(path), "-o", str(out)])
    assert result.exit_code == 1
    assert "styles.a.font.colour: unknown field" in result.output
    assert not out.exists()
