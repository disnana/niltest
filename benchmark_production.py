"""
本番環境（PRODUCTION=true）でのゼロコスト検証ベンチマーク。
インポート前に環境変数を設定することで、
デコレータが最初からパススルーとして機能します。
"""
import os
os.environ["PRODUCTION"] = "true"  # ← インポート前に設定するのが重要

import timeit
from niltest import scenario, expect


# PRODUCTION=true 状態でデコレート
# -> @scenario は func をそのまま返すのでラッパーは一切存在しない
@scenario("ベンチマーク用決済処理")
def process_payment(amount: int, user_status: str) -> str:
    if expect:  # expect は False なので絶対に入らない
        expect.case("テスト",
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


N = 1_000_000
t_raw = timeit.timeit(lambda: raw(5_000, "member"), number=N)
t_dec = timeit.timeit(lambda: process_payment(5_000, "member"), number=N)

print(f"[niltest 本番ゼロコスト検証] {N:,} 回呼び出し")
print(f"  プレーン関数 : {t_raw:.4f}s")
print(f"  niltest 関数 : {t_dec:.4f}s")
diff_ns = (t_dec - t_raw) / N * 1e9
print(f"  1回あたり差分: {diff_ns:.1f}ns")
print()
if abs(diff_ns) < 10:
    print("  -> 誤差範囲内。ゼロコストを実証済み。")
else:
    print(f"  -> 警告: {diff_ns:.1f}ns のオーバーヘッドが検出されました。")
