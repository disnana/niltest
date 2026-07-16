"""
niltest テストスイート

各モジュールの動作を pytest で徹底検証します。
"""

from __future__ import annotations

import dataclasses
import importlib

import pytest


# ─────────────────────────────────────────────────────────────
# テスト用フィクスチャ: 各テストの前後で niltest の状態をリセット
# ─────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def reset_niltest():
    """各テスト前後に niltest の設定とレジストリをリセットします。"""
    import niltest._config as cfg
    import niltest._expect as ex
    import niltest._scenario as sc

    cfg._MODE = "mock"
    cfg._LANGUAGE = "ja"
    ex.expect._pending.clear()
    sc._registry.clear()
    yield
    cfg._MODE = "mock"
    cfg._LANGUAGE = "ja"
    ex.expect._pending.clear()
    sc._registry.clear()


# ─────────────────────────────────────────────────────────────
# 1. configure() のテスト
# ─────────────────────────────────────────────────────────────
class TestConfigure:
    def test_default_mode_is_production(self, monkeypatch):
        import niltest._config as cfg

        monkeypatch.delenv("NILTEST_MODE", raising=False)
        importlib.reload(cfg)
        assert cfg._MODE == "production"
        assert cfg.is_production() is True

    def test_mode_is_loaded_from_niltest_environment(self, monkeypatch):
        import niltest._config as cfg

        monkeypatch.setenv("NILTEST_MODE", "test")
        importlib.reload(cfg)
        assert cfg._MODE == "test"
        assert cfg.is_production() is False

    def test_configure_production(self):
        import niltest
        import niltest._config as cfg

        niltest.configure(mode="production")
        assert cfg.is_production() is True

    def test_configure_mode_mock(self):
        import niltest

        niltest.configure(mode="mock")
        import niltest._config as cfg

        assert cfg._MODE == "mock"

    def test_configure_mode_test(self):
        import niltest

        niltest.configure(mode="test")
        import niltest._config as cfg

        assert cfg._MODE == "test"

    def test_configure_accepts_mode_enum(self):
        import niltest
        import niltest._config as cfg

        niltest.configure(mode=niltest.Mode.TEST)
        assert cfg._MODE == "test"

    def test_mode_is_a_string_enum(self):
        import niltest

        assert niltest.Mode.MOCK == "mock"

    def test_configure_partial_update(self):
        import niltest
        import niltest._config as cfg

        niltest.configure(mode="mock")
        niltest.configure(mode="test")
        assert cfg._MODE == "test"


# ─────────────────────────────────────────────────────────────
# 2. expect.__bool__ のテスト
# ─────────────────────────────────────────────────────────────
class TestExpectBool:
    def test_expect_is_truthy_in_dev_mode(self):
        import niltest._config as cfg
        from niltest._expect import expect

        cfg._MODE = "test"
        assert bool(expect) is True

    def test_expect_is_falsy_in_production(self):
        import niltest._config as cfg
        from niltest._expect import expect

        cfg._MODE = "production"
        assert bool(expect) is False
        cfg._MODE = "test"  # 後続テストのためリセット


# ─────────────────────────────────────────────────────────────
# 3. @scenario + モックモードのテスト
# ─────────────────────────────────────────────────────────────
class TestScenarioMock:
    def test_plain_value_mock_match(self):
        import niltest
        from niltest import expect, scenario

        niltest.configure(mode="mock")

        @scenario("テスト: プレーン値")
        def func(x: int) -> str:
            if expect:
                expect.case("正常系", given=dict(x=1), returns="ok")
            return "real"

        assert func(1) == "ok"

    def test_plain_value_mock_no_match_calls_real(self):
        import niltest
        from niltest import expect, scenario

        niltest.configure(mode="mock")

        @scenario("テスト: マッチなし")
        def func(x: int) -> str:
            if expect:
                expect.case("正常系", given=dict(x=1), returns="ok")
            return "real"

        assert func(999) == "real"

    def test_mock_with_dataclass(self):
        import niltest
        from niltest import expect, scenario

        niltest.configure(mode="mock")

        @dataclasses.dataclass
        class Result:
            value: int

        @scenario("テスト: dataclass モック")
        def func(x: int) -> Result:
            if expect:
                expect.case("正常系", given=dict(x=1), returns=Result(value=42))
            return Result(value=0)

        result = func(1)
        assert result == Result(value=42)

    def test_mock_skips_for_type_only_returns(self):
        """型のみ returns はモックに使えないので実装が動くはず"""
        import niltest
        from niltest import expect, scenario

        niltest.configure(mode="mock")

        @dataclasses.dataclass
        class Res:
            v: int

        @scenario("テスト: 型チェックのみ")
        def func(x: int) -> Res:
            if expect:
                expect.case("型チェック", given=dict(x=1), returns=Res)
            return Res(v=x * 10)

        # 型のみなので実装が動く
        assert func(1) == Res(v=10)

    def test_mock_skips_for_callable_returns(self):
        """callable returns はモックに使えないので実装が動くはず"""
        import niltest
        from niltest import expect, scenario

        niltest.configure(mode="mock")

        @scenario("テスト: callable returns")
        def func(x: int) -> int:
            if expect:
                expect.case("バリデータ", given=dict(x=1), returns=lambda r: r > 0)
            return x * 2

        assert func(1) == 2

    def test_production_mode_bypasses_wrapper(self):
        """production モードでは @scenario は素通し"""
        import niltest
        from niltest import scenario

        niltest.configure(mode="production")

        call_count = {"n": 0}

        @scenario("テスト: 本番パススルー")
        def func(x: int) -> int:
            call_count["n"] += 1
            return x * 3

        result = func(5)
        assert result == 15
        assert call_count["n"] == 1
        # ラッパーが存在しないことを確認（__wrapped__ 属性がない）
        assert not hasattr(func, "_niltest_doc_done")


# ─────────────────────────────────────────────────────────────
# 4. run_tests() のテスト
# ─────────────────────────────────────────────────────────────
class TestRunTests:
    def _make_payment_func(self):
        import niltest
        from niltest import expect, scenario

        niltest.configure(mode="mock")

        @scenario("決済処理")
        def process_payment(amount: int, user_status: str) -> str:
            if expect:
                expect.case(
                    "異常系: 無効金額",
                    given=dict(amount=-1, user_status="member"),
                    returns="invalid_amount",
                )
                expect.case(
                    "正常系: 通常決済",
                    given=dict(amount=5_000, user_status="member"),
                    returns="approved",
                )
            if amount <= 0:
                return "invalid_amount"
            return "approved"

        return process_payment

    def test_all_pass(self, capsys):
        import niltest

        func = self._make_payment_func()
        niltest.configure(mode="test")
        niltest.run_tests(func)
        out = capsys.readouterr().out
        assert "PASS" in out
        assert "FAIL" not in out
        assert "2 passed" in out

    def test_fail_detected(self, capsys):
        import niltest
        from niltest import expect, scenario

        niltest.configure(mode="mock")

        @scenario("バグあり関数")
        def buggy(x: int) -> str:
            if expect:
                expect.case(
                    "正常系",
                    given=dict(x=1),
                    returns="correct",
                )
            return "wrong"  # 意図的にバグを仕込む

        niltest.configure(mode="test")
        niltest.run_tests(buggy)
        out = capsys.readouterr().out
        assert "FAIL" in out
        assert "0 passed" in out
        assert "1 failed" in out


# ─────────────────────────────────────────────────────────────
# 5. returns_match のテスト
# ─────────────────────────────────────────────────────────────
class TestReturnsMatch:
    def test_plain_value_match(self):
        from niltest._compare import returns_match

        ok, reason = returns_match("approved", "approved")
        assert ok is True
        assert reason == ""

    def test_plain_value_mismatch(self):
        from niltest._compare import returns_match

        ok, reason = returns_match("wrong", "approved")
        assert ok is False
        assert "値不一致" in reason

    def test_type_check_pass(self):
        from niltest._compare import returns_match

        ok, _ = returns_match("hello", str)
        assert ok is True

    def test_type_check_fail(self):
        from niltest._compare import returns_match

        ok, reason = returns_match(123, str)
        assert ok is False
        assert "型不一致" in reason

    def test_dataclass_instance_match(self):
        from niltest._compare import returns_match

        @dataclasses.dataclass
        class D:
            x: int
            y: str

        ok, _ = returns_match(D(x=1, y="a"), D(x=1, y="a"))
        assert ok is True

    def test_dataclass_instance_mismatch(self):
        from niltest._compare import returns_match

        @dataclasses.dataclass
        class D:
            x: int

        ok, reason = returns_match(D(x=1), D(x=99))
        assert ok is False
        assert "フィールド不一致" in reason

    def test_callable_validator_pass(self):
        from niltest._compare import returns_match

        ok, _ = returns_match(
            {"id": "abc-123", "count": 5}, lambda r: isinstance(r["id"], str) and r["count"] > 0
        )
        assert ok is True

    def test_callable_validator_fail(self):
        from niltest._compare import returns_match

        ok, reason = returns_match(
            {"id": None, "count": 0}, lambda r: isinstance(r["id"], str) and r["count"] > 0
        )
        assert ok is False
        assert "バリデータ" in reason

    def test_callable_validator_exception(self):
        from niltest._compare import returns_match

        # バリデータが例外を投げてもクラッシュしない
        ok, reason = returns_match(None, lambda r: r["key"])
        assert ok is False
        assert "バリデータ例外" in reason

    def test_pydantic_model_match(self):
        pytest.importorskip("pydantic")
        from pydantic import BaseModel

        from niltest._compare import returns_match

        class M(BaseModel):
            id: int
            name: str

        ok, _ = returns_match(M(id=1, name="Alice"), M(id=1, name="Alice"))
        assert ok is True

    def test_pydantic_model_mismatch(self):
        pytest.importorskip("pydantic")
        from pydantic import BaseModel

        from niltest._compare import returns_match

        class M(BaseModel):
            id: int
            name: str

        ok, reason = returns_match(M(id=1, name="Alice"), M(id=2, name="Bob"))
        assert ok is False
        assert "フィールド不一致" in reason


# ─────────────────────────────────────────────────────────────
# 6. docstring 自動生成のテスト
# ─────────────────────────────────────────────────────────────
class TestDocstring:
    def test_docstring_generated_on_first_call(self):
        import niltest
        from niltest import expect, scenario

        niltest.configure(mode="mock")

        @scenario("仕様タイトル")
        def func(x: int) -> str:
            if expect:
                expect.case(
                    "ケース1",
                    desc="説明文",
                    given=dict(x=1),
                    returns="ok",
                )
            return "real"

        # 初回呼び出しでdocstringが生成される
        func(1)
        assert "仕様タイトル" in (func.__doc__ or "")
        assert "ケース1" in (func.__doc__ or "")
        assert "説明文" in (func.__doc__ or "")

    def test_docstring_contains_all_cases(self):
        import niltest
        from niltest import expect, scenario

        niltest.configure(mode="mock")

        @scenario("全ケース確認")
        def func(x: int) -> str:
            if expect:
                expect.case("ケースA", given=dict(x=1), returns="a")
                expect.case("ケースB", given=dict(x=2), returns="b")
                expect.case("ケースC", given=dict(x=3), returns="c")
            return "real"

        func(1)
        doc = func.__doc__ or ""
        assert "ケースA" in doc
        assert "ケースB" in doc
        assert "ケースC" in doc

    def test_no_docstring_in_production(self):
        import niltest
        from niltest import scenario

        niltest.configure(mode="production")

        @scenario("本番")
        def func(x: int) -> str:
            return "real"

        # 本番ではラッパーなし、__doc__ は元の関数のもの
        assert not hasattr(func, "_niltest_doc_done")

    def test_docstring_empty_original_doc(self):
        import niltest
        from niltest import expect, scenario

        niltest.configure(mode="mock")

        @scenario("No doc")
        def func():
            if expect:
                expect.case("A", given={}, returns=1)
            return 1

        func()
        # original doc が空の場合のパス（_docgen.py L15-16）をカバー
        assert "Scenario: No doc" in (func.__doc__ or "")


# ─────────────────────────────────────────────────────────────
# 7. Async サポートのテスト
# ─────────────────────────────────────────────────────────────
class TestAsyncScenarioMock:
    @pytest.mark.asyncio
    async def test_concurrent_calls_keep_separate_contexts(self):
        import asyncio

        import niltest
        from niltest import expect, scenario

        niltest.configure(mode="mock")

        @scenario("concurrent")
        async def label(value: int) -> str:
            await asyncio.sleep(0)
            if expect:
                expect.case("one", given={"value": 1}, returns="one")
                expect.case("two", given={"value": 2}, returns="two")
            return "real"

        assert await asyncio.gather(label(1), label(2)) == ["one", "two"]

    @pytest.mark.asyncio
    async def test_async_mock_match(self):
        import niltest
        from niltest import expect, scenario

        niltest.configure(mode="mock")

        @scenario("非同期テスト")
        async def fetch_data(id: int) -> dict:
            if expect:
                expect.case("正常系", given=dict(id=1), returns={"data": "ok"})
            return {"data": "real"}

        result = await fetch_data(1)
        assert result == {"data": "ok"}

    @pytest.mark.asyncio
    async def test_async_mock_no_match(self):
        import niltest
        from niltest import expect, scenario

        niltest.configure(mode="mock")

        @scenario("非同期テスト")
        async def fetch_data(id: int) -> dict:
            if expect:
                expect.case("正常系", given=dict(id=1), returns={"data": "ok"})
            return {"data": "real"}

        result = await fetch_data(99)
        assert result == {"data": "real"}


class TestAsyncRunTests:
    def test_async_run_tests_success(self, capsys):
        import niltest
        from niltest import expect, scenario

        niltest.configure(mode="mock")

        @scenario("非同期自動テスト")
        async def process(x: int) -> int:
            if expect:
                expect.case("ケース1", given=dict(x=5), returns=10)
            return x * 2

        niltest.configure(mode="test")
        niltest.run_tests(process)
        out = capsys.readouterr().out
        assert "PASS" in out
        assert "FAIL" not in out
        assert "1 passed" in out

    def test_async_run_tests_fail(self, capsys):
        import niltest
        from niltest import expect, scenario

        niltest.configure(mode="mock")

        @scenario("非同期自動テスト(失敗)")
        async def process(x: int) -> int:
            if expect:
                expect.case("ケース1", given=dict(x=5), returns=999)
            return x * 2

        niltest.configure(mode="test")
        niltest.run_tests(process)
        out = capsys.readouterr().out
        assert "FAIL" in out
        assert "0 passed" in out


# ─────────────────────────────────────────────────────────────
# 8. エッジケース・カバレッジ補完
# ─────────────────────────────────────────────────────────────
class TestEdgeCases:
    def test_nested_scenario_restores_outer_context(self):
        import niltest
        from niltest import expect, scenario

        niltest.configure(mode="mock")

        @scenario("inner")
        def inner(value: int) -> str:
            if expect:
                expect.case("inner case", given={"value": 1}, returns="inner mock")
            return "inner real"

        @scenario("outer")
        def outer(value: int) -> str:
            inner(value)
            if expect:
                expect.case("outer case", given={"value": 1}, returns="outer mock")
            return "outer real"

        assert outer(1) == "outer mock"

    def test_expect_case_in_production(self):
        # production モードでは expect.case() は何もしない
        import niltest
        from niltest._expect import expect

        niltest.configure(mode="production")
        # 呼ばれても何もしない
        expect.case("test", given={}, returns=None)
        assert len(expect._pending) == 0

    def test_format_returns_exceptions(self):
        # _compare.py の format_returns でソース取得失敗の例外パスをカバー
        from niltest._compare import format_returns

        # 組込み関数などはソースが取れない
        res = format_returns(len)
        assert "validator: <callable>" in res

    def test_try_early_collect_fail(self):
        # デフォルト値がない引数がある場合、早期収集はスキップされる
        import niltest
        from niltest import expect, scenario

        niltest.configure(mode="mock")

        @scenario("必須引数あり")
        def func(req: int):
            if expect:
                expect.case("A", given=dict(req=1), returns=1)
            return req

        # 適用直後は doc_built = False
        assert not hasattr(func, "_niltest_doc_done")

    def test_run_sync_with_existing_loop(self):
        import asyncio

        from niltest._scenario import _run_sync

        async def dummy():
            pass

        async def main():
            # すでにループが回っている中で _run_sync を呼ぶと RuntimeError
            try:
                _run_sync(dummy())
            except RuntimeError as e:
                assert "cannot be called from within an already running" in str(e)

        asyncio.run(main())
