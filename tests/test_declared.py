from __future__ import annotations

import niltest
from niltest import case, docs, scenario


def test_declared_cases_do_not_execute_function_during_decoration() -> None:
    calls = 0

    @scenario("shipping")
    @docs(case("premium", given={"premium": True}, returns=0))
    def shipping(premium: bool) -> int:
        nonlocal calls
        calls += 1
        return 500

    assert calls == 0
    assert "premium" in (shipping.__doc__ or "")


def test_declared_cases_mock_and_test(monkeypatch) -> None:
    @scenario("shipping")
    @docs(
        case("premium", given={"premium": True}, returns=0),
        case("standard", given={"premium": False}, returns=500),
    )
    def shipping(premium: bool) -> int:
        return 0 if premium else 500

    monkeypatch.setattr(niltest._config, "_MODE", "MOCK")
    assert shipping(True) == 0
    monkeypatch.setattr(niltest._config, "_MODE", "NORMAL")
    assert shipping.run_tests().passed == 2  # type: ignore[attr-defined]


def test_declared_production_returns_original_function(monkeypatch) -> None:
    monkeypatch.setattr(niltest._config, "_PRODUCTION", True)

    def original(value: int) -> int:
        return value + 1

    decorated = scenario("identity")(docs(case("one", given={"value": 1}, returns=2))(original))
    assert decorated is original
    assert decorated(1) == 2
