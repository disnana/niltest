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
- NILTEST_MODE=production : 安全な既定値。デコレータはパススルー
- NILTEST_MODE=mock       : given に一致した引数のとき returns を即返却
- niltest run      : 定義されたケースで自動テストを実行
"""

from typing import Protocol, cast

from ._config import configure
from ._declared import case, docs
from ._expect import expect
from ._i18n import register_locale
from ._result import CaseResult, RunResult, ScenarioResult
from ._scenario import _registry, scenario
from ._typing import TypeExpectation, conforms_to


class _RunnableScenario(Protocol):
    def run_tests(self) -> ScenarioResult: ...


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
            results.append(cast(_RunnableScenario, t).run_tests())
    return RunResult(tuple(results))


__all__ = [
    "CaseResult",
    "RunResult",
    "ScenarioResult",
    "TypeExpectation",
    "case",
    "configure",
    "conforms_to",
    "docs",
    "expect",
    "register_locale",
    "run_tests",
    "scenario",
]
__version__ = "1.2.0"
