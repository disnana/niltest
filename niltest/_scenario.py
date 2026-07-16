from __future__ import annotations
import asyncio
import functools
import inspect
from typing import Any, Callable, TypeVar

from . import _config
from ._expect import Expect, _MockReturn, _local, expect
from ._docgen import build_docstring
from ._case import _Case
from ._compare import returns_match
from ._i18n import translate

F = TypeVar("F", bound=Callable[..., Any])

# @scenario でデコレートされた全関数を追跡するレジストリ
_registry: dict[str, Any] = {}


def scenario(title: str) -> Callable[[F], F]:
    """
    関数を仕様検証可能な対象としてマークするデコレータ。

    - PRODUCTION=True  : 元の関数をそのまま返します（ラッパーなし・ゼロコスト）
    - PRODUCTION=False : ラッパーを適用し、モック・テスト・docstring生成を有効化します
    """
    def decorator(func: F) -> F:
        if _config._PRODUCTION:
            return func

        cases: list[_Case] = []
        doc_built = False
        is_async = inspect.iscoroutinefunction(func)

        def _collect_all_cases(*args: Any, **kwargs: Any) -> None:
            nonlocal doc_built, cases
            prev_mode = _config._MODE
            _config._MODE = "__DOC_SCAN__"
            expect._pending.clear()
            _local.call_kwargs = None

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
            if cases:
                wrapper.__doc__ = build_docstring(
                    func.__doc__ or "", title, cases
                )
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
                    if p.kind not in (
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

                if not doc_built:
                    _collect_all_cases(*args, **kwargs)

                _local.call_kwargs = call_kwargs
                try:
                    return await func(*args, **kwargs)
                except _MockReturn as e:
                    return e.value
                finally:
                    _local.call_kwargs = None
                    expect._pending.clear()
        else:
            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                nonlocal doc_built
                sig = inspect.signature(func)
                bound = sig.bind(*args, **kwargs)
                bound.apply_defaults()
                call_kwargs = dict(bound.arguments)

                if not doc_built:
                    _collect_all_cases(*args, **kwargs)

                _local.call_kwargs = call_kwargs
                try:
                    return func(*args, **kwargs)
                except _MockReturn as e:
                    return e.value
                finally:
                    _local.call_kwargs = None
                    expect._pending.clear()

        # ─── 自動テスト実行用メソッドをラッパーに付与 ───
        def run_tests() -> None:
            nonlocal cases
            if not cases:
                _collect_via_probe()
            if not cases:
                print(f"[niltest] '{title}': {translate(_config._LANGUAGE, 'no_cases')}")
                return

            print(f"\n[niltest] {translate(_config._LANGUAGE, 'scenario')}: {title}")
            print("-" * 50)
            passed = 0
            failed = 0

            prev_mode = _config._MODE
            _config._MODE = "TEST"

            for c in cases:
                try:
                    if is_async:
                        actual = _run_sync(func(**c.given))
                    else:
                        actual = func(**c.given)

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
            print(f"\n  {translate(_config._LANGUAGE, 'result', passed=passed, failed=failed)}")

        wrapper.run_tests = run_tests  # type: ignore[attr-defined]

        # 早期収集を試行
        _try_early_collect()

        _registry[func.__qualname__] = wrapper
        return wrapper  # type: ignore[return-value]

    return decorator


def _run_sync(coro: Any) -> Any:
    """非同期コルーチンを同期的に実行して結果を返します。"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    else:
        # Jupyterやuvicornなど既存のループ上で呼ばれた場合、nest_asyncio等がないとブロックできない。
        # 通常の pytest や CLI での実行を想定し、ここではタスクを生成して同期待ちする簡易ハックは行わず、
        # asyncio.run に近い挙動ができるか試みる。通常はここには来ない。
        raise RuntimeError("run_tests() cannot be called from within an already running asyncio event loop.")
