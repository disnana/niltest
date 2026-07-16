from __future__ import annotations
import threading
from typing import Any

from . import _config
from ._case import _Case
from ._compare import can_use_as_mock


class _MockReturn(BaseException):
    """モック値を関数の外に運ぶための専用例外。BaseException を使うことで
    通常の except Exception: に捕捉されるのを防ぎます。"""

    def __init__(self, value: Any) -> None:
        self.value = value


# スレッドセーフな呼び出しコンテキスト
_local = threading.local()


class Expect:
    """
    開発・テストモード時に仕様ケースを収集・評価するオブジェクト。

    本番環境（PRODUCTION=True）では `bool(expect)` が False を返すため、
    `if expect:` ブロックごとスキップされ、実行時コストはゼロになります。
    """

    def __init__(self) -> None:
        # 直近の呼び出しで登録されたケース一覧（docstring生成・テスト実行に使用）
        self._pending: list[_Case] = []

    # ------------------------------------------------------------------
    # bool 評価 — 本番では False、開発では True
    # ------------------------------------------------------------------
    def __bool__(self) -> bool:
        return not _config._PRODUCTION

    # ------------------------------------------------------------------
    # 仕様ケースの登録
    # ------------------------------------------------------------------
    def case(
        self,
        name: str,
        *,
        desc: str = "",
        given: dict[str, Any],
        returns: Any,
    ) -> None:
        """
        仕様ケースを1件登録します。

        Args:
            name:    ケース名（例: "正常系: 管理者ユーザー"）
            desc:    ケースの説明（任意）
            given:   代表的な入力引数を kwargs 形式で指定
            returns: そのときに期待する戻り値
        """
        if _config._PRODUCTION:
            return

        c = _Case(name, desc=desc, given=given, returns=returns)
        self._pending.append(c)

        # MOCK モード: 現在の呼び出し引数と given が一致したら即返却
        # __DOC_SCAN__ モードや、callable/型のみ returns はモックとして使えないのでスキップ
        if _config._MODE == "MOCK" and can_use_as_mock(returns):
            ctx: dict | None = getattr(_local, "call_kwargs", None)
            if ctx is not None and ctx == given:
                raise _MockReturn(returns)

    def _flush(self) -> list[_Case]:
        """登録済みケースを取り出してリセットします（docstring生成用）。"""
        cases, self._pending = self._pending, []
        return cases


# パッケージ全体で共有するシングルトン
expect = Expect()
