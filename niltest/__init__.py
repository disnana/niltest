"""
niltest
=======
本番環境ではラッパーなしで動作しながら、
コードの可視性・テスト・モックを一体化する Python ライブラリ。

クイックスタート
----------------
    from niltest import scenario, expect

    @scenario("ユーザー取得の仕様")
    def get_user(user_id: int, role: str = "member") -> dict:
        if expect:
            expect.case("正常系: 一般ユーザー",
                desc="一般ユーザーIDで呼び出した場合",
                given=dict(user_id=1, role="member"),
                returns={"id": 1, "name": "Alice"}
            )
            expect.case("正常系: 管理者",
                desc="管理者IDで呼び出した場合",
                given=dict(user_id=99, role="admin"),
                returns={"id": 99, "name": "Admin"}
            )

        # 実際の実装
        return {"id": user_id, "name": "Real User"}

動作モード
----------
- PRODUCTION=true  : デコレータはパススルー、仕様ブロックは真偽判定だけでスキップ
- MODE=MOCK        : given に一致した引数のとき returns を即返却
- niltest run      : 定義されたケースで自動テストを実行
"""

from ._config import configure
from ._expect import expect
from ._i18n import register_locale
from ._scenario import scenario, _registry
from ._result import CaseResult, RunResult, ScenarioResult


def run_tests(*funcs: object) -> RunResult:
    """
    指定した @scenario 関数、またはすべての登録済み @scenario 関数に対して
    定義済みの expect.case をテストとして自動実行します。

    使い方:
        niltest.run_tests()               # 全シナリオを実行
        niltest.run_tests(my_function)    # 特定の関数だけ実行
    """
    targets = list(funcs) if funcs else list(_registry.values())
    results: list[ScenarioResult] = []
    for t in targets:
        if hasattr(t, "run_tests"):
            results.append(t.run_tests())  # type: ignore[union-attr]
    return RunResult(tuple(results))


__all__ = [
    "CaseResult", "RunResult", "ScenarioResult", "configure", "expect",
    "register_locale", "scenario", "run_tests",
]
__version__ = "0.1.0"
