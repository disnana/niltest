from __future__ import annotations

import asyncio
import functools
import inspect
from collections.abc import Callable
from typing import Any, TypeVar

from . import _config
from ._case import _Case
from ._compare import can_use_as_mock, returns_match
from ._docgen import build_docstring
from ._expect import _local, _MockReturn, expect
from ._i18n import translate
from ._result import CaseResult, ScenarioResult
from ._typing import prepare_case_inputs

F = TypeVar("F", bound=Callable[..., Any])

# @scenario でデコレートされた全関数を追跡するレジストリ
_registry: dict[str, Any] = {}


def scenario(title: str) -> Callable[[F], F]:
    """
    関数を仕様検証可能な対象としてマークするデコレータ。

    - ``mode="production"`` : 元の関数をそのまま返します（ラッパーなし）
    - ``mode="test"`` / ``"mock"`` : ラッパーを適用し、仕様機能を有効化します
    """

    def decorator(func: F) -> F:
        declared_cases = list(getattr(func, "__niltest_cases__", ()))
        if _config.is_production():
            return func

        cases: list[_Case] = declared_cases
        doc_built = bool(declared_cases)
        is_async = inspect.iscoroutinefunction(func)

        def _apply_declared_mock(call_kwargs: dict[str, Any]) -> None:
            if _config._MODE != "mock":
                return
            for declared in declared_cases:
                if declared.given == call_kwargs and can_use_as_mock(declared.returns):
                    raise _MockReturn(declared.returns)

        def _collect_all_cases(*args: Any, **kwargs: Any) -> None:
            nonlocal doc_built, cases
            prev_mode = _config._MODE
            _config._MODE = "__doc_scan__"
            pending_token = expect._push_pending()
            call_token = _local.push(None)

            try:
                # ドライラン実行。async の場合はイベントループで回す
                if is_async:
                    _run_sync(func(*args, **kwargs))
                else:
                    func(*args, **kwargs)
            except _MockReturn:
                pass
            except Exception:
                pass
            finally:
                _config._MODE = prev_mode
                cases = expect._flush()
                _local.pop(call_token)
                expect._pop_pending(pending_token)
            if cases:
                wrapper.__doc__ = build_docstring(func.__doc__ or "", title, cases)
            doc_built = True

        def _try_early_collect() -> None:
            """全引数にデフォルト値がある場合や引数なしの場合、ロード時にケース収集を試みる"""
            try:
                sig = inspect.signature(func)
                for p in sig.parameters.values():
                    if p.default is inspect.Parameter.empty and p.kind not in (
                        inspect.Parameter.VAR_POSITIONAL,
                        inspect.Parameter.VAR_KEYWORD,
                    ):
                        return
                _collect_all_cases()
            except Exception:
                pass

        def _collect_via_probe() -> None:
            """ダミー引数(None)を使って収集を試みる"""
            try:
                sig = inspect.signature(func)
                dummy = {
                    name: None
                    for name, p in sig.parameters.items()
                    if p.kind
                    not in (
                        inspect.Parameter.VAR_POSITIONAL,
                        inspect.Parameter.VAR_KEYWORD,
                    )
                }
                _collect_all_cases(**dummy)
            except Exception:
                pass

        # ─── 実行時ラッパーの定義 ───
        if is_async:

            @functools.wraps(func)
            async def wrapper(*args: Any, **kwargs: Any) -> Any:
                nonlocal doc_built
                sig = inspect.signature(func)
                bound = sig.bind(*args, **kwargs)
                bound.apply_defaults()
                call_kwargs = dict(bound.arguments)
                pending_token = expect._push_pending()

                if not doc_built:
                    _collect_all_cases(*args, **kwargs)

                call_token = _local.push(call_kwargs)
                try:
                    _apply_declared_mock(call_kwargs)
                    return await func(*args, **kwargs)
                except _MockReturn as e:
                    return e.value
                finally:
                    _local.pop(call_token)
                    expect._pop_pending(pending_token)
        else:

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                nonlocal doc_built
                sig = inspect.signature(func)
                bound = sig.bind(*args, **kwargs)
                bound.apply_defaults()
                call_kwargs = dict(bound.arguments)
                pending_token = expect._push_pending()

                if not doc_built:
                    _collect_all_cases(*args, **kwargs)

                call_token = _local.push(call_kwargs)
                try:
                    _apply_declared_mock(call_kwargs)
                    return func(*args, **kwargs)
                except _MockReturn as e:
                    return e.value
                finally:
                    _local.pop(call_token)
                    expect._pop_pending(pending_token)

        # ─── 自動テスト実行用メソッドをラッパーに付与 ───
        def run_tests() -> ScenarioResult:
            nonlocal cases
            if not cases:
                _collect_via_probe()
            if not cases:
                print(f"[niltest] '{title}': {translate(_config._LANGUAGE, 'no_cases')}")
                return ScenarioResult(title)

            print(f"\n[niltest] {translate(_config._LANGUAGE, 'scenario')}: {title}")
            print("-" * 50)
            passed = 0
            failed = 0
            results: list[CaseResult] = []

            prev_mode = _config._MODE
            _config._MODE = "test"

            try:
                for c in cases:
                    prepared_given, input_issues = prepare_case_inputs(func, c.given)
                    if input_issues:
                        failed += 1
                        reason = "invalid case input: " + "; ".join(input_issues)
                        results.append(CaseResult(c.name, "error", reason))
                        print(f"  [ERROR] {c.name}: {reason}")
                        continue
                    try:
                        if is_async:
                            actual = _run_sync(func(**prepared_given))
                        else:
                            actual = func(**prepared_given)

                        ok, reason = returns_match(actual, c.returns)
                        status = "PASS" if ok else "FAIL"
                        if ok:
                            passed += 1
                            results.append(CaseResult(c.name, "passed"))
                        else:
                            failed += 1
                            results.append(CaseResult(c.name, "failed", reason))
                        print(f"  [{status}] {c.name}")
                        if not ok:
                            print(f"         {reason}")
                    except Exception as e:
                        failed += 1
                        reason = f"{type(e).__name__}: {e}"
                        results.append(CaseResult(c.name, "error", reason))
                        print(f"  [ERROR] {c.name}: {e}")
            finally:
                _config._MODE = prev_mode
            print(f"\n  {translate(_config._LANGUAGE, 'result', passed=passed, failed=failed)}")
            return ScenarioResult(title, tuple(results))

        wrapper.run_tests = run_tests  # type: ignore[attr-defined]

        def get_cases() -> tuple[_Case, ...]:
            nonlocal cases
            if not cases:
                _collect_via_probe()
            return tuple(cases)

        wrapper.__niltest_title__ = title  # type: ignore[attr-defined]
        wrapper.__niltest_original__ = func  # type: ignore[attr-defined]
        wrapper.__niltest_get_cases__ = get_cases  # type: ignore[attr-defined]

        if declared_cases:
            wrapper.__doc__ = build_docstring(func.__doc__ or "", title, declared_cases)

        # 早期収集を試行
        _try_early_collect()

        _registry[f"{func.__module__}.{func.__qualname__}"] = wrapper
        return wrapper  # type: ignore[return-value]

    return decorator


def _run_sync(coro: Any) -> Any:
    """非同期コルーチンを同期的に実行して結果を返します。"""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        # Jupyterやuvicornなど既存のループ上で呼ばれた場合、nest_asyncio等がないとブロックできない。
        # 通常の pytest や CLI での実行を想定し、ここではタスクを生成して同期待ちする簡易ハックは行わず、
        # asyncio.run に近い挙動ができるか試みる。通常はここには来ない。
        close = getattr(coro, "close", None)
        if close is not None:
            close()
        raise RuntimeError(
            "run_tests() cannot be called from within an already running asyncio event loop."
        )
