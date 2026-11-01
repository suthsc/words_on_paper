"""Cascading style resolution for raw configuration dicts.

Texts can pick up settings from three places, applied lowest to highest
precedence:

1. ``defaults`` - applied to every text
2. ``styles`` named by the text's ``style`` key (a name or a list of names),
   in the order listed; each style's own ``extends`` chain is applied first
3. the text's inline fields

Nested mappings (``font``, ``position``, ``effects.*``) merge key by key;
scalars and lists replace. Resolution happens on plain dicts before Pydantic
validation, so nothing downstream needs to know about styles.

All functions here are pure: they never mutate their inputs.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping
from typing import Any, Optional

EXTENDS_KEY = "extends"
STYLE_KEY = "style"


class StyleError(ValueError):
    """Raised when styles cannot be resolved (unknown name, cycle, bad type)."""


def deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    """Return a new dict with ``override`` merged onto ``base``.

    Where both sides hold a mapping, they are merged recursively; otherwise
    the override value replaces the base value. The result shares no mutable
    structure with either input.
    """
    result: dict[str, Any] = copy.deepcopy(dict(base))
    for key, value in override.items():
        existing = result.get(key)
        if isinstance(existing, Mapping) and isinstance(value, Mapping):
            result[key] = deep_merge(existing, value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _as_name_list(value: Any, what: str) -> list[str]:
    """Normalize a str-or-list-of-str field into a list, or raise StyleError."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        return list(value)
    raise StyleError(f"{what} must be a style name or a list of style names")


def resolve_style(
    name: str,
    styles: Mapping[str, Any],
    _stack: tuple[str, ...] = (),
    _cache: Optional[dict[str, dict[str, Any]]] = None,
) -> dict[str, Any]:
    """Return the fully-expanded body of style ``name`` (without ``extends``).

    Parents listed in ``extends`` are applied in order, so later parents win
    over earlier ones and the style's own keys win over all parents.

    Raises:
        StyleError: on an unknown style, a cycle, or a malformed style.
    """
    cache = {} if _cache is None else _cache
    if name in _stack:
        chain = " -> ".join((*_stack, name))
        raise StyleError(f"style cycle: {chain}")
    if name in cache:
        return copy.deepcopy(cache[name])
    if name not in styles:
        raise StyleError(f"unknown style '{name}'")

    body = styles[name]
    if not isinstance(body, Mapping):
        raise StyleError(f"style '{name}' must be a mapping")

    stack = (*_stack, name)
    resolved: dict[str, Any] = {}
    if EXTENDS_KEY in body:
        parents = _as_name_list(body[EXTENDS_KEY], f"styles.{name}.extends")
        for parent in parents:
            resolved = deep_merge(resolved, resolve_style(parent, styles, stack, cache))
    own = {k: v for k, v in body.items() if k != EXTENDS_KEY}
    resolved = deep_merge(resolved, own)

    cache[name] = resolved
    return copy.deepcopy(resolved)


def resolve_text(
    text: Mapping[str, Any],
    defaults: Mapping[str, Any],
    styles: Mapping[str, Any],
    _cache: Optional[dict[str, dict[str, Any]]] = None,
) -> dict[str, Any]:
    """Return ``text`` with defaults and its referenced styles applied.

    The ``style`` key is kept on the result so the origin stays visible.
    """
    cache = {} if _cache is None else _cache
    resolved = deep_merge({}, defaults)
    if text.get(STYLE_KEY) is not None:
        for name in _as_name_list(text[STYLE_KEY], STYLE_KEY):
            resolved = deep_merge(resolved, resolve_style(name, styles, _cache=cache))
    return deep_merge(resolved, text)


def resolve_config(raw: Any) -> Any:
    """Return a copy of a raw config dict with every text fully expanded.

    ``defaults`` and ``styles`` are left in place for inspection. Input that
    isn't shaped like a config (non-dict, non-list ``texts``, non-dict text
    entries) is passed through untouched so Pydantic can report it.

    Raises:
        StyleError: if styles can't be resolved; the message names the text.
    """
    if not isinstance(raw, Mapping):
        return raw
    defaults = raw.get("defaults") or {}
    styles = raw.get("styles") or {}
    texts = raw.get("texts")
    if not isinstance(defaults, Mapping):
        raise StyleError("defaults must be a mapping")
    if not isinstance(styles, Mapping):
        raise StyleError("styles must be a mapping")

    result = copy.deepcopy(dict(raw))
    if not isinstance(texts, list) or not (defaults or styles or _uses_style(texts)):
        return result

    cache: dict[str, dict[str, Any]] = {}
    resolved_texts: list[Any] = []
    for i, text in enumerate(texts):
        if not isinstance(text, Mapping):
            resolved_texts.append(copy.deepcopy(text))
            continue
        try:
            resolved_texts.append(resolve_text(text, defaults, styles, cache))
        except StyleError as exc:
            raise StyleError(f"texts[{i}]: {exc}") from exc
    result["texts"] = resolved_texts
    return result


def _uses_style(texts: list[Any]) -> bool:
    """True if any text references a style (so unknown refs still error)."""
    return any(isinstance(t, Mapping) and t.get(STYLE_KEY) is not None for t in texts)
