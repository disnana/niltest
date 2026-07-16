from __future__ import annotations
import functools
import inspect
from typing import Any, Callable, TypeVar

from . import _config
from ._expect import Expect, _MockReturn, _local, expect
from ._docgen import build_docstring
from ._case import _Case
from ._compare import returns_match

F = TypeVar("F", bound=Callable[..., Any])

# @scenario でデコレートされた全関数を追跡するレジストリ
_registry: dict[str, "_ScenarioWrapper"] = {}


class _ScenarioWrapper:
    """scenario デコレータが生成するラッパー。ケース情報も保持します。"""

    def __init__(self, func: Callable, title: str) -> None:
        self._func = func
        self._title = title
        self._cases: list[_Case] = []
        self._doc_built = False
        functools.update_wrapper(self, func)

        # デコレータ適用時点でケースを収集できるか試みる
        # (引数なしで呼べる・または全引数にデフォルト値がある場合のみ成功する)
        self._try_early_collect()

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        # positional args を kwargs に展開して統一
        sig = inspect.signature(self._func)
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        call_kwargs = dict(bound.arguments)

        # 初回呼び出し時: ドライランで全ケースを収集してドックストリング生成
        if not self._doc_built:
            self._collect_all_cases(*args, **kwargs)

        # 本番呼び出し（MOCKモードならケース登録と同時にマッチング）
        _local.call_kwargs = call_kwargs
        try:
            return self._func(*args, **kwargs)
        except _MockReturn as e:
            return e.value
        finally:
            _local.call_kwargs = None
            expect._pending.clear()

    def _try_early_collect(self) -> None:
        """デコレータ適用時にケース収集を試みます（全引数にデフォルト値がある場合のみ成功）。"""
        try:
            sig = inspect.signature(self._func)
            # デフォルト値のない必須引数が存在する場合はスキップ
            for p in sig.parameters.values():
                if p.default is inspect.Parameter.empty and p.kind not in (
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
                ):
                    return
            self._collect_all_cases()
        except Exception:
            pass

    def _collect_all_cases(self, *args: Any, **kwargs: Any) -> None:
        """ドライランで全 expect.case を収集し、docstring を生成します。"""
        prev_mode = _config._MODE
        _config._MODE = "__DOC_SCAN__"
        expect._pending.clear()
        _local.call_kwargs = None  # マッチングを無効にして全ケースを収集

        try:
            self._func(*args, **kwargs)
        except Exception:
            pass  # 実装側の例外は無視（ドキュメント収集目的のため）
        finally:
            _config._MODE = prev_mode

        self._cases = expect._flush()
        if self._cases:
            self.__doc__ = build_docstring(
                self._func.__doc__ or "", self._title, self._cases
            )
        self._doc_built = True

    def run_tests(self) -> None:
        """
        定義されたすべての expect.case を使って実際の関数を実行し、
        returns と照合して自動テストを行います。
        """
        # ケース未収集 → 最初のケースの given を使ってドライランで収集
        if not self._cases:
            self._collect_from_first_given()
        if not self._cases:
            print(f"[niltest] '{self._title}': ケースが収集できませんでした。")
            return

        print(f"\n[niltest] Scenario: {self._title}")
        print("-" * 50)
        passed = 0
        failed = 0

        prev_mode = _config._MODE
        _config._MODE = "TEST"

        for c in self._cases:
            try:
                actual = self._func(**c.given)
                ok, reason = returns_match(actual, c.returns)
                status = "PASS" if ok else "FAIL"
                if ok:
                    passed += 1
                else:
                    failed += 1
                print(f"  [{status}] {c.name}")
                if not ok:
                    print(f"         {reason}")
            except Exception as e:
                failed += 1
                print(f"  [ERROR] {c.name}: {e}")

        _config._MODE = prev_mode
        print(f"\n  結果: {passed} passed / {failed} failed")

    def _collect_from_first_given(self) -> None:
        """ケース未収集時: 最初の expect.case の given でドライランして全ケースを収集します。"""
        # __DOC_SCAN__ モードで1回だけ呼び出して全ケースを収集する
        # given の中身で実装側の分岐がどこを通るかは関係ない（全 expect.case が登録される）
        prev_mode = _config._MODE
        _config._MODE = "__DOC_SCAN__"
        expect._pending.clear()
        _local.call_kwargs = None

        # まず任意の given を使って 1 回呼び出す（全 case が登録される）
        # _pending に何もなければ収集不可
        try:
            # シグネチャの各引数に None を渡して呼び出しを試みる
            sig = inspect.signature(self._func)
            dummy = {
                name: None
                for name, p in sig.parameters.items()
                if p.kind not in (
                    inspect.Parameter.VAR_POSITIONAL,
                    inspect.Parameter.VAR_KEYWORD,
                )
            }
            self._func(**dummy)
        except Exception:
            pass
        finally:
            _config._MODE = prev_mode

        self._cases = expect._flush()
        if self._cases:
            self.__doc__ = build_docstring(
                self._func.__doc__ or "", self._title, self._cases
            )
            self._doc_built = True


def scenario(title: str) -> Callable[[F], F]:
    """
    関数を仕様検証可能な対象としてマークするデコレータ。

    - PRODUCTION=True  : 元の関数をそのまま返します（ラッパーなし・ゼロコスト）
    - PRODUCTION=False : _ScenarioWrapper でラップし、モック・テスト・docstring生成を有効化
    """
    def decorator(func: F) -> F:
        if _config._PRODUCTION:
            return func
        wrapper = _ScenarioWrapper(func, title)
        _registry[func.__qualname__] = wrapper
        return wrapper  # type: ignore[return-value]
    return decorator
