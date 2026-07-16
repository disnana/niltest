"""
02. Dataclass / Pydantic のサポート

複雑なデータ構造を扱う場合、インスタンスをそのまま returns に渡せます。
モック時はそのインスタンスがそのまま返され、
テスト時は自動的に辞書化(asdict/model_dump)されてフィールド比較が行われます。
"""
from dataclasses import dataclass
import niltest
from niltest import scenario, expect

niltest.configure(mode="MOCK")

@dataclass
class UserInfo:
    id: int
    name: str
    status: str

@scenario("ユーザー情報取得 API")
def fetch_user(user_id: int) -> UserInfo:
    if expect:
        expect.case("正常系: 有効なユーザー",
            given=dict(user_id=1),
            returns=UserInfo(id=1, name="Alice", status="active"),
        )
        expect.case("異常系: 退会済み",
            given=dict(user_id=99),
            returns=UserInfo(id=99, name="Unknown", status="deleted"),
        )

    # 実装ロジック
    if user_id == 1:
        return UserInfo(id=1, name="Alice", status="active")
    return UserInfo(id=user_id, name="Unknown", status="deleted")

if __name__ == "__main__":
    print("=== モックモード実行 ===")
    print("User 1:", fetch_user(1))
    
    print("\n=== テスト実行 ===")
    niltest.configure(mode="TEST")
    niltest.run_tests(fetch_user)
