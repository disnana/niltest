import locale
import os

from ._i18n import is_registered_locale, normalize_locale

# グローバル設定（モジュール内で共有する状態）
_PRODUCTION: bool = os.getenv("PRODUCTION", "false").lower() == "true"
_MODE: str = os.getenv("MODE", "MOCK").upper()


def _detect_language() -> str:
    """Choose the user's OS language, with English as a predictable fallback."""
    configured = os.getenv("NILTEST_LANGUAGE")
    if configured:
        candidate = normalize_locale(configured)
        return candidate if is_registered_locale(candidate) else "en"

    # ``getlocale`` uses the platform's configured locale on Windows, macOS,
    # and Linux.  It can be unset on minimal containers, hence the fallback.
    system_locale = locale.getlocale()[0]
    if system_locale:
        candidate = normalize_locale(system_locale)
        return candidate if is_registered_locale(candidate) else "en"
    return "en"


_LANGUAGE: str = _detect_language()


def configure(
    production: bool | None = None,
    mode: str | None = None,
    language: str | None = None,
) -> None:
    """
    niltestの動作モードを設定します。

    Args:
        production: Trueにするとすべての検証コードがパススルーされます。
                    デフォルトは環境変数 PRODUCTION から自動ロード。
        mode:       "MOCK" または "TEST"。
                    デフォルトは環境変数 MODE から自動ロード。
        language:   出力言語。未指定なら OS の言語設定を使い、取得できない場合は英語。
                    NILTEST_LANGUAGE で明示的に指定することも可能。
    """
    global _PRODUCTION, _MODE, _LANGUAGE
    if production is not None:
        _PRODUCTION = production
    if mode is not None:
        normalized_mode = mode.upper()
        if normalized_mode not in {"MOCK", "TEST"}:
            raise ValueError("mode must be either 'MOCK' or 'TEST'.")
        _MODE = normalized_mode
    if language is not None:
        normalized_language = normalize_locale(language)
        if not is_registered_locale(normalized_language):
            raise ValueError(
                f"Unknown language '{language}'. Register it with register_locale() first."
            )
        _LANGUAGE = normalized_language
