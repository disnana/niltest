from __future__ import annotations
import dataclasses
from typing import Any


def returns_match(actual: Any, expected: Any) -> tuple[bool, str]:
    """
    actual と expected を比較してマッチするか判定します。

    expected の種類に応じて比較方法を自動選択:
      - callable (lambda等)         → expected(actual) が truthy か
      - クラス型 (type)              → isinstance チェック（型のみ確認）
      - Pydantic BaseModel インスタンス → model_dump() でフィールド比較
      - dataclass インスタンス        → asdict() でフィールド比較
      - それ以外                      → == で値比較

    Returns:
        (matched: bool, reason: str)  reason は FAIL 時の説明文
    """
    # ── パターン 0: callable（バリデータ関数・lambda）───────────────
    # ランダムデータや複雑な条件のとき: returns=lambda r: r["id"] > 0
    if callable(expected) and not isinstance(expected, type):
        try:
            matched = bool(expected(actual))
        except Exception as e:
            return False, f"バリデータ例外: {e}"
        reason = "" if matched else f"バリデータが False を返しました\n  actual={actual!r}"
        return matched, reason

    # ── パターン 1: クラス型が渡された → isinstance チェックのみ ────
    if isinstance(expected, type):
        matched = isinstance(actual, expected)
        reason = (
            ""
            if matched
            else f"型不一致: actual={type(actual).__name__}, expected={expected.__name__}"
        )
        return matched, reason

    # ── パターン 2: Pydantic BaseModel インスタンス ──────────────────
    if _is_pydantic(expected):
        exp_dict = expected.model_dump() if hasattr(expected, "model_dump") else expected.dict()
        act_dict = (
            actual.model_dump() if hasattr(actual, "model_dump")
            else actual.dict() if hasattr(actual, "dict")
            else actual
        )
        matched = act_dict == exp_dict
        reason = "" if matched else f"フィールド不一致:\n  expected={exp_dict}\n  actual  ={act_dict}"
        return matched, reason

    # ── パターン 3: dataclass インスタンス ───────────────────────────
    if _is_dataclass_instance(expected):
        exp_dict = dataclasses.asdict(expected)
        act_dict = dataclasses.asdict(actual) if _is_dataclass_instance(actual) else actual
        matched = act_dict == exp_dict
        reason = "" if matched else f"フィールド不一致:\n  expected={exp_dict}\n  actual  ={act_dict}"
        return matched, reason

    # ── パターン 4: プレーンな値（デフォルト） ───────────────────────
    matched = actual == expected
    reason = "" if matched else f"値不一致:\n  expected={expected!r}\n  actual  ={actual!r}"
    return matched, reason


def can_use_as_mock(returns: Any) -> bool:
    """
    returns がモック値として使えるか判定します。
    callable / 型のみ の場合はモック値として返す意味がないため False。
    """
    if isinstance(returns, type):
        return False          # 型チェックのみ → 実際の値がない
    if callable(returns) and not isinstance(returns, type):
        return False          # バリデータ関数 → 返す値がない
    return True


def format_returns(returns: Any) -> str:
    """docstring 用に returns を読みやすい文字列にフォーマットします。"""
    if isinstance(returns, type):
        return f"{returns.__name__} (型チェックのみ)"
    if callable(returns):
        import inspect
        try:
            src = inspect.getsource(returns).strip()
            src = " ".join(src.split())
            return f"validator: {src}"
        except Exception:
            return "validator: <callable>"
    if _is_pydantic(returns):
        d = returns.model_dump() if hasattr(returns, "model_dump") else returns.dict()
        return f"{type(returns).__name__}({d})"
    if _is_dataclass_instance(returns):
        return f"{type(returns).__name__}({dataclasses.asdict(returns)})"
    return repr(returns)


def _is_pydantic(obj: Any) -> bool:
    """Pydantic v1 / v2 どちらにも対応。型ではなくインスタンスかどうかで判定。"""
    return not isinstance(obj, type) and (hasattr(obj, "model_dump") or hasattr(obj, "dict"))


def _is_dataclass_instance(obj: Any) -> bool:
    return dataclasses.is_dataclass(obj) and not isinstance(obj, type)
