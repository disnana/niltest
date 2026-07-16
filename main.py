"""
niltest デモ - returns の全パターンを確認
"""
import dataclasses
import uuid
import niltest
from niltest import scenario, expect

niltest.configure(production=False, mode="MOCK")


# ── dataclass の定義 ──────────────────────────────────────────
@dataclasses.dataclass
class UserData:
    id: int
    name: str
    role: str


# ─────────────────────────────────────────────────────────────
# ① 通常の決済処理（プレーン値 returns）
# ─────────────────────────────────────────────────────────────
@scenario("決済処理のビジネスロジック仕様")
def process_payment(amount: int, user_status: str) -> str:
    if expect:
        expect.case("異常系: 無効な決済金額",
            desc="決済金額が 0 以下の場合は即エラーを返す",
            given=dict(amount=-1, user_status="member"),
            returns="invalid_amount",           # ← プレーン値
        )
        expect.case("正常系: プレミアムユーザー",
            desc="プレミアム会員は金額にかかわらず即承認",
            given=dict(amount=150_000, user_status="premium"),
            returns="approved",                  # ← プレーン値
        )

    if amount <= 0:
        return "invalid_amount"
    if user_status == "premium":
        return "approved"
    return "approved"


# ─────────────────────────────────────────────────────────────
# ② dataclass インスタンスを returns に渡す
# ─────────────────────────────────────────────────────────────
@scenario("ユーザー取得の仕様（dataclass returns）")
def get_user(user_id: int) -> UserData:
    if expect:
        expect.case("正常系: 一般ユーザー",
            desc="一般ユーザーの情報を dataclass で返す",
            given=dict(user_id=1),
            returns=UserData(id=1, name="Alice", role="member"),   # ← dataclass
        )
        expect.case("正常系: 管理者",
            desc="管理者の情報を dataclass で返す",
            given=dict(user_id=99),
            returns=UserData(id=99, name="Admin", role="admin"),    # ← dataclass
        )

    return UserData(id=user_id, name="Alice" if user_id == 1 else "Admin",
                    role="member" if user_id == 1 else "admin")


# ─────────────────────────────────────────────────────────────
# ③ 型のみを渡す（ランダムなフィールドを含む場合などに）
# ─────────────────────────────────────────────────────────────
@scenario("ユーザー作成の仕様（型チェックのみ）")
def create_user(name: str) -> UserData:
    if expect:
        expect.case("正常系: ユーザー作成",
            desc="作成結果は UserData 型であることだけを確認する",
            given=dict(name="Alice"),
            returns=UserData,      # ← 型のみ（isinstance チェック）
        )

    return UserData(id=hash(name) % 9999, name=name, role="member")


# ─────────────────────────────────────────────────────────────
# ④ callable（lambda）を returns に渡す（ランダムデータ対応）
# ─────────────────────────────────────────────────────────────
@scenario("トークン生成の仕様（バリデータ returns）")
def generate_token(user_id: int) -> dict:
    if expect:
        expect.case("正常系: トークン生成",
            desc="生成されたトークンは UUID 形式で user_id を含む",
            given=dict(user_id=42),
            returns=lambda r: (          # ← バリデータ。ランダムな値でも検証できる
                isinstance(r.get("token"), str)
                and len(r["token"]) == 36      # UUID の長さ
                and r.get("user_id") == 42
            ),
        )

    return {
        "token": str(uuid.uuid4()),
        "user_id": user_id,
    }


# ─────────────────────────────────────────────────────────────
# テスト実行（given/returns を使って自動検証）
# ─────────────────────────────────────────────────────────────
print("=" * 55)
print("モックモード動作確認")
print("=" * 55)
print("process_payment(-1, 'member') :", process_payment(-1, "member"))
print("process_payment(150000, 'premium') :", process_payment(150_000, "premium"))
print("get_user(1) :", get_user(1))
print("get_user(99) :", get_user(99))
print()

print("=" * 55)
print("自動テスト（全シナリオ）")
print("=" * 55)
niltest.configure(mode="TEST")
niltest.run_tests()
