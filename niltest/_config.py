import locale
import os
from enum import Enum

from ._i18n import is_registered_locale, normalize_locale

_VALID_MODES = frozenset({"production", "test", "mock"})


class Mode(str, Enum):
    """Runtime modes accepted by :func:`configure`."""

    PRODUCTION = "production"
    TEST = "test"
    MOCK = "mock"


# Safe by default: importing an application must never make declared values act
# as mocks unless the application explicitly opts in.
_MODE: str = os.getenv("NILTEST_MODE", "production").lower()
if _MODE not in _VALID_MODES:
    raise ValueError(f"NILTEST_MODE must be one of: production, test, mock. Received {_MODE!r}.")


def _detect_language() -> str:
    """Choose the user's OS language, with English as a predictable fallback."""
    configured = os.getenv("NILTEST_LANGUAGE")
    if configured:
        candidate = normalize_locale(configured)
        return candidate if is_registered_locale(candidate) else "en"

    # ``getlocale`` uses the platform's configured locale on Windows, macOS,
    # and Linux. It can be unset on minimal containers, hence the fallback.
    system_locale = locale.getlocale()[0]
    if system_locale:
        candidate = normalize_locale(system_locale)
        return candidate if is_registered_locale(candidate) else "en"
    return "en"


_LANGUAGE: str = _detect_language()


def is_production() -> bool:
    """Return whether niltest must be completely inert at runtime."""
    return _MODE == "production"


def configure(mode: Mode | str | None = None, language: str | None = None) -> None:
    """Configure niltest before importing modules decorated with ``@scenario``.

    Args:
        mode: Prefer :class:`Mode` (for example, ``Mode.TEST``). The strings
            ``"production"``, ``"test"``, and ``"mock"`` remain supported.
        language: Output language. Defaults to the operating-system language,
            with English as the fallback. ``NILTEST_LANGUAGE`` can set it at
            process start.
    """
    global _MODE, _LANGUAGE
    if mode is not None:
        normalized_mode = mode.value if isinstance(mode, Mode) else mode.lower()
        if normalized_mode not in _VALID_MODES:
            allowed = ", ".join(sorted(_VALID_MODES))
            raise ValueError(f"mode must be one of: {allowed}.")
        _MODE = normalized_mode
    if language is not None:
        normalized_language = normalize_locale(language)
        if not is_registered_locale(normalized_language):
            raise ValueError(
                f"Unknown language '{language}'. Register it with register_locale() first."
            )
        _LANGUAGE = normalized_language
