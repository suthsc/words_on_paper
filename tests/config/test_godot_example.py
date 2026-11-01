"""Equivalence test for the styled Waiting for Godot example."""

from __future__ import annotations

from pathlib import Path

from words_on_paper.config.loader import load_config

ROOT = Path(__file__).resolve().parents[2]
STYLED = ROOT / "examples" / "waiting_for_godot_full_scene.yaml"
FLAT = ROOT / "tests" / "fixtures" / "godot_flat.yaml"


def test_styled_godot_matches_flat_original() -> None:
    """The cascade reproduces the hand-written flat config exactly.

    tests/fixtures/godot_flat.yaml is the example as it was before styles;
    every resolved text must equal its flat counterpart (ignoring `style`).
    """
    styled = load_config(STYLED)
    flat = load_config(FLAT)

    assert styled.video == flat.video
    assert styled.background == flat.background
    assert len(styled.texts) == len(flat.texts)
    for i, (s, f) in enumerate(zip(styled.texts, flat.texts)):
        assert s.model_dump(exclude={"style"}) == f.model_dump(exclude={"style"}), i
    assert styled.get_video_duration() == flat.get_video_duration()


def test_styled_godot_uses_styles() -> None:
    """Sanity check: the example actually exercises defaults, styles and extends."""
    styled = load_config(STYLED)
    assert styled.defaults
    assert any("extends" in body for body in styled.styles.values())
    assert any(isinstance(t.style, list) for t in styled.texts)
