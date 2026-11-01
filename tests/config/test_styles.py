"""Tests for the cascading style resolver."""

from __future__ import annotations

import copy

import pytest

from words_on_paper.config.styles import (
    StyleError,
    deep_merge,
    resolve_config,
    resolve_style,
    resolve_text,
)


class TestDeepMerge:
    """Tests for deep_merge()."""

    def test_deep_merge_nested_font(self) -> None:
        """Nested dicts merge key by key, so unset keys survive."""
        base = {"font": {"family": "Courier", "size": 40}}
        override = {"font": {"color": "#FF0000"}}
        assert deep_merge(base, override) == {
            "font": {"family": "Courier", "size": 40, "color": "#FF0000"}
        }

    def test_deep_merge_nested_position_and_effects(self) -> None:
        """Merging recurses through several levels (effects.scale.*)."""
        base = {
            "position": {"mode": "relative", "x": 0.15},
            "effects": {"scale": {"enabled": True, "initial_scale": 0.5}},
        }
        override = {
            "position": {"y": 0.4},
            "effects": {"scale": {"initial_scale": 0.8}, "typing": {"enabled": True}},
        }
        assert deep_merge(base, override) == {
            "position": {"mode": "relative", "x": 0.15, "y": 0.4},
            "effects": {
                "scale": {"enabled": True, "initial_scale": 0.8},
                "typing": {"enabled": True},
            },
        }

    def test_deep_merge_scalar_replaces(self) -> None:
        """Scalars in the override replace the base value."""
        assert deep_merge({"z_index": 1, "a": 2}, {"z_index": 5}) == {
            "z_index": 5,
            "a": 2,
        }

    def test_deep_merge_list_replaces(self) -> None:
        """Lists are replaced wholesale, not concatenated."""
        assert deep_merge({"tags": [1, 2]}, {"tags": [3]}) == {"tags": [3]}

    def test_deep_merge_dict_replaced_by_scalar(self) -> None:
        """A non-dict override replaces a dict base value."""
        assert deep_merge({"style": {"a": 1}}, {"style": "x"}) == {"style": "x"}

    def test_deep_merge_does_not_mutate(self) -> None:
        """Neither input is mutated, and the result shares no nested dicts."""
        base = {"font": {"family": "Courier"}}
        override = {"font": {"size": 10}}
        base_copy = copy.deepcopy(base)
        override_copy = copy.deepcopy(override)
        result = deep_merge(base, override)
        result["font"]["family"] = "Changed"
        assert base == base_copy
        assert override == override_copy


class TestResolveStyle:
    """Tests for resolve_style()."""

    def test_resolve_style_plain(self) -> None:
        """A style without extends resolves to itself (minus extends)."""
        styles = {"a": {"z_index": 3}}
        assert resolve_style("a", styles) == {"z_index": 3}

    def test_resolve_style_extends_single(self) -> None:
        """A style inherits from its parent and overrides it."""
        styles = {
            "base": {"font": {"family": "Courier", "size": 40}},
            "vlad": {"extends": "base", "font": {"color": "#1A5490"}},
        }
        assert resolve_style("vlad", styles) == {
            "font": {"family": "Courier", "size": 40, "color": "#1A5490"}
        }

    def test_resolve_style_extends_multi(self) -> None:
        """With several parents, later parents win; the style itself wins last."""
        styles = {
            "a": {"z_index": 1, "font": {"family": "A"}},
            "b": {"z_index": 2, "font": {"size": 20}},
            "c": {"extends": ["a", "b"], "font": {"color": "#000000"}},
        }
        assert resolve_style("c", styles) == {
            "z_index": 2,
            "font": {"family": "A", "size": 20, "color": "#000000"},
        }

    def test_resolve_style_extends_transitive(self) -> None:
        """Extends chains are followed through several levels."""
        styles = {
            "root": {"fade_in_duration": 0.5, "z_index": 1},
            "mid": {"extends": "root", "z_index": 2},
            "leaf": {"extends": "mid", "display_duration": 4.0},
        }
        assert resolve_style("leaf", styles) == {
            "fade_in_duration": 0.5,
            "z_index": 2,
            "display_duration": 4.0,
        }

    def test_resolve_style_unknown(self) -> None:
        """An unknown style name raises StyleError naming the style."""
        with pytest.raises(StyleError, match="unknown style 'nope'"):
            resolve_style("nope", {"a": {}})

    def test_resolve_style_unknown_parent(self) -> None:
        """An unknown parent in extends raises StyleError."""
        with pytest.raises(StyleError, match="unknown style 'ghost'"):
            resolve_style("a", {"a": {"extends": "ghost"}})

    def test_resolve_style_cycle(self) -> None:
        """A cycle raises StyleError showing the chain."""
        styles = {"a": {"extends": "b"}, "b": {"extends": "a"}}
        with pytest.raises(StyleError, match="a -> b -> a"):
            resolve_style("a", styles)

    def test_resolve_style_self_cycle(self) -> None:
        """A style extending itself is a cycle."""
        with pytest.raises(StyleError, match="a -> a"):
            resolve_style("a", {"a": {"extends": "a"}})

    def test_resolve_style_not_a_mapping(self) -> None:
        """A style whose body isn't a mapping raises StyleError."""
        with pytest.raises(StyleError, match="must be a mapping"):
            resolve_style("a", {"a": "oops"})

    def test_resolve_style_bad_extends_type(self) -> None:
        """extends must be a string or a list of strings."""
        with pytest.raises(StyleError, match="extends"):
            resolve_style("a", {"a": {"extends": 3}})

    def test_resolve_style_does_not_mutate(self) -> None:
        """The styles mapping is not mutated."""
        styles = {"a": {"font": {"size": 1}}, "b": {"extends": "a", "z_index": 2}}
        styles_copy = copy.deepcopy(styles)
        resolve_style("b", styles)
        assert styles == styles_copy


class TestResolveText:
    """Tests for resolve_text()."""

    def test_resolve_text_precedence(self) -> None:
        """defaults < styles (in listed order) < inline."""
        defaults = {"z_index": 0, "font": {"family": "Arial", "size": 30}}
        styles = {
            "s1": {"z_index": 1, "font": {"size": 40}},
            "s2": {"z_index": 2, "font": {"color": "#111111"}},
        }
        text = {"content": "hi", "style": ["s1", "s2"], "font": {"size": 50}}
        assert resolve_text(text, defaults, styles) == {
            "content": "hi",
            "style": ["s1", "s2"],
            "z_index": 2,
            "font": {"family": "Arial", "size": 50, "color": "#111111"},
        }

    def test_resolve_text_style_list_order(self) -> None:
        """Later styles in the list override earlier ones."""
        styles = {
            "red": {"font": {"color": "#FF0000"}},
            "blue": {"font": {"color": "#0000FF"}},
        }
        a = resolve_text({"content": "x", "style": ["red", "blue"]}, {}, styles)
        b = resolve_text({"content": "x", "style": ["blue", "red"]}, {}, styles)
        assert a["font"]["color"] == "#0000FF"
        assert b["font"]["color"] == "#FF0000"

    def test_resolve_text_style_string(self) -> None:
        """style may be a single string."""
        styles = {"s": {"z_index": 7}}
        assert resolve_text({"content": "x", "style": "s"}, {}, styles)["z_index"] == 7

    def test_resolve_text_defaults_only(self) -> None:
        """With no style, only defaults apply."""
        result = resolve_text({"content": "x"}, {"fade_in_duration": 0.2}, {})
        assert result == {"content": "x", "fade_in_duration": 0.2}

    def test_resolve_text_unknown_style(self) -> None:
        """Referencing an unknown style raises StyleError."""
        with pytest.raises(StyleError, match="unknown style 'missing'"):
            resolve_text({"content": "x", "style": "missing"}, {}, {})

    def test_resolve_text_bad_style_type(self) -> None:
        """style must be a string or list of strings."""
        with pytest.raises(StyleError, match="style"):
            resolve_text({"content": "x", "style": 5}, {}, {})


class TestResolveConfig:
    """Tests for resolve_config()."""

    def test_resolve_config_passthrough(self) -> None:
        """A config without defaults/styles comes back unchanged."""
        raw = {
            "video": {"width": 100, "height": 100, "fps": 10},
            "texts": [{"content": "a", "font": {"size": 10}}],
        }
        assert resolve_config(raw) == raw

    def test_resolve_config_expands_texts(self) -> None:
        """Texts are expanded; defaults and styles are kept for inspection."""
        raw = {
            "defaults": {"fade_in_duration": 0.5},
            "styles": {"big": {"font": {"size": 99}}},
            "texts": [{"content": "a", "style": "big"}, {"content": "b"}],
        }
        result = resolve_config(raw)
        assert result["texts"] == [
            {
                "content": "a",
                "style": "big",
                "fade_in_duration": 0.5,
                "font": {"size": 99},
            },
            {"content": "b", "fade_in_duration": 0.5},
        ]
        assert result["defaults"] == raw["defaults"]
        assert result["styles"] == raw["styles"]

    def test_resolve_config_error_names_text_index(self) -> None:
        """Errors in a text mention which text failed."""
        raw = {"texts": [{"content": "a"}, {"content": "b", "style": "nope"}]}
        with pytest.raises(StyleError, match=r"texts\[1\]"):
            resolve_config(raw)

    def test_resolve_config_does_not_mutate(self) -> None:
        """The raw config is not mutated."""
        raw = {
            "defaults": {"font": {"family": "Courier"}},
            "styles": {"s": {"extends": "t"}, "t": {"z_index": 1}},
            "texts": [{"content": "a", "style": "s", "font": {"size": 5}}],
        }
        raw_copy = copy.deepcopy(raw)
        resolve_config(raw)
        assert raw == raw_copy

    def test_resolve_config_non_dict_passthrough(self) -> None:
        """Non-dict input is returned as is (Pydantic reports the error)."""
        assert resolve_config("nonsense") == "nonsense"

    def test_resolve_config_diamond_extends(self) -> None:
        """A shared ancestor reached twice (diamond) is not mistaken for a cycle."""
        raw = {
            "styles": {
                "root": {"font": {"family": "Courier"}},
                "left": {"extends": "root", "z_index": 1},
                "right": {"extends": "root", "z_index": 2},
                "both": {"extends": ["left", "right"]},
            },
            "texts": [
                {"content": "a", "style": "both"},
                {"content": "b", "style": "left"},
            ],
        }
        texts = resolve_config(raw)["texts"]
        assert texts[0]["z_index"] == 2
        assert texts[0]["font"] == {"family": "Courier"}
        assert texts[1]["z_index"] == 1

    @pytest.mark.parametrize("key", ["defaults", "styles"])
    def test_resolve_config_bad_section_type(self, key: str) -> None:
        """defaults and styles must be mappings."""
        with pytest.raises(StyleError, match=f"{key} must be a mapping"):
            resolve_config({key: ["x"], "texts": []})

    def test_resolve_config_non_dict_text_passthrough(self) -> None:
        """Non-dict text entries are left for Pydantic to reject."""
        raw = {"defaults": {"z_index": 1}, "texts": ["oops", {"content": "a"}]}
        assert resolve_config(raw)["texts"] == ["oops", {"content": "a", "z_index": 1}]
