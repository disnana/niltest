"""
01. 基本的な使い方 (プレーン値)

最もシンプルな、通常の戻り値(文字列や数値など)をモック・テストする例です。
"""
import niltest
from niltest import scenario, expect

# モックモードで起動
niltest.configure(production=False, mode="MOCK")

@scenario("割引計算の仕様")
def calculate_discount(price: int, customer_type: str) -> int:
    if expect:
        expect.case("正常系: プレミアム会員",
            desc="プレミアム会員は常に 20% 引き",
            given=dict(price=1000, customer_type="premium"),
            returns=800,
        )
        expect.case("正常系: 一般会員",
            desc="一般会員は割引なし",
            given=dict(price=1000, customer_type="normal"),
            returns=1000,
        )

    # 実際の計算ロジック
    if customer_type == "premium":
        return int(price * 0.8)
    return price

if __name__ == "__main__":
    print("=== モックモード実行 ===")
    print("premium (1000) ->", calculate_discount(1000, "premium"))  # 実装を通らず 800
    print("normal (1000)  ->", calculate_discount(1000, "normal"))   # 実装を通らず 1000
    
    print("\n=== テスト実行 ===")
    # 自動テスト実行
    niltest.configure(mode="TEST")
    niltest.run_tests(calculate_discount)
