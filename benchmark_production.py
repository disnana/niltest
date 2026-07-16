"""
本番環境（NILTEST_MODE=production）でのオーバーヘッド検証ベンチマーク。
インポート前に環境変数を設定することで、
デコレータが最初からパススルーとして機能します。
"""

import os
from collections.abc import Callable

os.environ["NILTEST_MODE"] = "production"  # ← インポート前に設定するのが重要

import timeit

from niltest import case, docs, expect, scenario


# NILTEST_MODE=production 状態でデコレート
# -> @scenario は func をそのまま返すのでラッパーは一切存在しない
@scenario("ベンチマーク用決済処理")
def process_payment(amount: int, user_status: str) -> str:
    if expect:  # expect は False なので絶対に入らない
        expect.case(
            "テスト",
            given=dict(amount=1, user_status="x"),
            returns="x",
        )
    if amount <= 0:
        return "invalid_amount"
    if user_status == "premium":
        return "approved"
    if amount >= 100_000:
        return "under_review"
    return "approved"


def raw(amount: int, user_status: str) -> str:
    if amount <= 0:
        return "invalid_amount"
    if user_status == "premium":
        return "approved"
    if amount >= 100_000:
        return "under_review"
    return "approved"


def _declared_process_payment(amount: int, user_status: str) -> str:
    if amount <= 0:
        return "invalid_amount"
    if user_status == "premium":
        return "approved"
    if amount >= 100_000:
        return "under_review"
    return "approved"


# 宣言型API: @docs はケースを関数外へ置くため、関数本体に if expect: がない。
declared_process_payment = scenario("宣言型ベンチマーク用決済処理")(
    docs(
        case(
            "通常会員",
            given={"amount": 5_000, "user_status": "member"},
            returns="approved",
        )
    )(_declared_process_payment)
)
assert declared_process_payment is _declared_process_payment


N = 1_000_000


def best_time(callable_: Callable[[], object]) -> float:
    return min(timeit.repeat(callable_, number=N, repeat=7))


t_raw = best_time(lambda: raw(5_000, "member"))
t_inline = best_time(lambda: process_payment(5_000, "member"))
t_declared = best_time(lambda: declared_process_payment(5_000, "member"))

print(f"[niltest 本番オーバーヘッド検証] {N:,} 回呼び出し")
print(f"  プレーン関数 : {t_raw:.4f}s")
print(f"  if expect: API: {t_inline:.4f}s")
print(f"  @docs API    : {t_declared:.4f}s")
inline_diff_ns = (t_inline - t_raw) / N * 1e9
declared_diff_ns = (t_declared - t_raw) / N * 1e9
print(f"  if expect: 差分: {inline_diff_ns:.1f}ns / 回")
print(f"  @docs 差分    : {declared_diff_ns:.1f}ns / 回")
print()
print("  -> どちらもデコレータのラッパーはありません。")
print(
    "  -> @docs APIは関数本体に if expect: も置かないため、呼び出し経路にniltest由来の分岐はありません。"
)
print("  -> 小さな正負の差分はCPU測定上の揺らぎです。ゼロコストの根拠は上の同一性assertです。")
