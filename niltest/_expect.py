from __future__ import annotations

from contextvars import ContextVar, Token
from typing import Any

from . import _config
from ._case import _Case
from ._compare import can_use_as_mock


class _MockReturn(BaseException):
    """モック値を関数の外に運ぶための専用例外。BaseException を使うことで
    通常の except Exception: に捕捉されるのを防ぎます。"""

    def __init__(self, value: Any) -> None:
        self.value = value


_call_kwargs: ContextVar[dict[str, Any] | None] = ContextVar("niltest_call_kwargs", default=None)
_pending_cases: ContextVar[list[_Case] | None] = ContextVar("niltest_pending_cases", default=None)


class _ExecutionContext:
    """Task-local call state that also works for threads and nested scenarios."""

    @property
    def call_kwargs(self) -> dict[str, Any] | None:
        return _call_kwargs.get()

    @call_kwargs.setter
    def call_kwargs(self, value: dict[str, Any] | None) -> None:
        _call_kwargs.set(value)

    def push(self, value: dict[str, Any] | None) -> Token[dict[str, Any] | None]:
        return _call_kwargs.set(value)

    def pop(self, token: Token[dict[str, Any] | None]) -> None:
        _call_kwargs.reset(token)


_local = _ExecutionContext()


class Expect:
    """
    開発・テストモード時に仕様ケースを収集・評価するオブジェクト。

    ``production`` モードでは `bool(expect)` が False を返すため、
    `if expect:` ブロックごとスキップされ、真偽判定だけが実行されます。
    """

    def __init__(self) -> None:
        # State is created lazily in the active context.
        pass

    @property
    def _pending(self) -> list[_Case]:
        pending = _pending_cases.get()
        if pending is None:
            pending = []
            _pending_cases.set(pending)
        return pending

    @_pending.setter
    def _pending(self, value: list[_Case]) -> None:
        _pending_cases.set(value)

    def _push_pending(self) -> Token[list[_Case] | None]:
        return _pending_cases.set([])

    def _pop_pending(self, token: Token[list[_Case] | None]) -> None:
        _pending_cases.reset(token)

    # ------------------------------------------------------------------
    # bool 評価 — 本番では False、開発では True
    # ------------------------------------------------------------------
    def __bool__(self) -> bool:
        return not _config.is_production()

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
        if _config.is_production():
            return

        c = _Case(name, desc=desc, given=given, returns=returns)
        self._pending.append(c)

        # MOCK モード: 現在の呼び出し引数と given が一致したら即返却
        # __DOC_SCAN__ モードや、callable/型のみ returns はモックとして使えないのでスキップ
        if _config._MODE == "mock" and can_use_as_mock(returns):
            ctx: dict[str, Any] | None = _local.call_kwargs
            if ctx is not None and ctx == given:
                raise _MockReturn(returns)

    def _flush(self) -> list[_Case]:
        """登録済みケースを取り出してリセットします（docstring生成用）。"""
        cases, self._pending = self._pending, []
        return cases


# パッケージ全体で共有するシングルトン
expect = Expect()
