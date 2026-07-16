import os

# グローバル設定（モジュール内で共有する状態）
_PRODUCTION: bool = os.getenv("PRODUCTION", "false").lower() == "true"
_MODE: str = os.getenv("MODE", "MOCK").upper()


def configure(production: bool | None = None, mode: str | None = None) -> None:
    """
    niltestの動作モードを設定します。

    Args:
        production: Trueにするとすべての検証コードがパススルーされます。
                    デフォルトは環境変数 PRODUCTION から自動ロード。
        mode:       "MOCK" または "TEST"。
                    デフォルトは環境変数 MODE から自動ロード。
    """
    global _PRODUCTION, _MODE
    if production is not None:
        _PRODUCTION = production
    if mode is not None:
        _MODE = mode.upper()
