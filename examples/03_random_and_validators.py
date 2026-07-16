"""
03. ランダムデータとバリデータのサポート

戻り値にランダムなUUIDやタイムスタンプが含まれていて、固定値でモックできない場合、
returns に `lambda` や `型(type)` を渡すことができます。

注意: `lambda` や型を渡したケースはモックとして返すことができないため、
モックモード時は実行がスキップされ、実際の実装が呼ばれます。
テストモード時は、バリデータとして機能します。
"""

import uuid

import niltest
from niltest import expect, scenario

niltest.configure(mode="mock")


@scenario("トークン生成")
def create_token(user_id: int) -> dict:
    if expect:
        # lambda をバリデータとして使うケース
        expect.case(
            "正常系: 辞書と中身の検証",
            given=dict(user_id=42),
            returns=lambda r: (
                isinstance(r.get("token"), str) and len(r["token"]) == 36 and r["user_id"] == 42
            ),
        )

    # 実装は毎回違うトークンを返す
    return {
        "token": str(uuid.uuid4()),
        "user_id": user_id,
    }


@scenario("ID生成")
def generate_id(prefix: str) -> str:
    if expect:
        # 型チェックだけを行うケース
        expect.case(
            "正常系: 型だけチェック",
            given=dict(prefix="usr"),
            returns=str,
        )

    return f"{prefix}_{uuid.uuid4().hex[:8]}"


if __name__ == "__main__":
    print("=== モックモード実行 ===")
    # モックには使えないため、実際の値が返る
    print("Token:", create_token(42))
    print("ID:", generate_id("usr"))

    print("\n=== テスト実行 ===")
    niltest.configure(mode="test")
    niltest.run_tests(create_token, generate_id)
