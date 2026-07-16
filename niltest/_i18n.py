"""Locale registry and translation helpers for niltest."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .locales.en import MESSAGES as EN_MESSAGES
from .locales.ja import MESSAGES as JA_MESSAGES

_catalogs: dict[str, dict[str, str]] = {
    "ja": dict(JA_MESSAGES),
    "en": dict(EN_MESSAGES),
}


def normalize_locale(locale: str) -> str:
    """Return a base locale; ``ja-JP`` and ``Japanese_Japan`` become ``ja``."""
    base = locale.replace("_", "-").lower().split("-", 1)[0]
    return {"japanese": "ja", "english": "en"}.get(base, base)


def register_locale(locale: str, messages: Mapping[str, str], *, overwrite: bool = False) -> None:
    """Register a complete application or plugin locale catalog."""
    key = normalize_locale(locale)
    required = set(EN_MESSAGES)
    missing, extra = required - set(messages), set(messages) - required
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing: {', '.join(sorted(missing))}")
        if extra:
            details.append(f"unknown: {', '.join(sorted(extra))}")
        raise ValueError(f"Invalid niltest locale '{locale}' ({'; '.join(details)}).")
    if key in _catalogs and not overwrite:
        raise ValueError(f"Locale '{key}' is already registered. Use overwrite=True to replace it.")
    _catalogs[key] = dict(messages)


def is_registered_locale(locale: str) -> bool:
    return normalize_locale(locale) in _catalogs


def translate(locale: str, message: str, **values: Any) -> str:
    """Translate a message key, falling back to English."""
    catalog = _catalogs.get(normalize_locale(locale), _catalogs["en"])
    return catalog.get(message, _catalogs["en"][message]).format(**values)
