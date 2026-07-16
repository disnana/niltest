from __future__ import annotations

import niltest
from niltest import case, docs, expect, scenario


def test_declared_case_accepts_expected_exception_and_match(monkeypatch) -> None:
    monkeypatch.setattr(niltest._config, "_MODE", "test")

    @scenario("withdrawal")
    @docs(
        case(
            "negative amount",
            given={"amount": -1},
            raises=ValueError,
            match="positive",
        )
    )
    def withdraw(amount: int) -> int:
        if amount < 0:
            raise ValueError("amount must be positive")
        return amount

    result = niltest.run_tests(withdraw).scenarios[0].cases[0]
    assert result.passed
    assert result.expected == "raises ValueError matching 'positive'"
    assert result.actual == "ValueError: amount must be positive"
    assert result.given == {"amount": -1}
    assert result.function.endswith(".withdraw")
    assert "test_exceptions.py:" in result.source
    payload = result.to_dict()
    assert payload["given"] == {"amount": -1}
    assert payload["expected"] == "raises ValueError matching 'positive'"


def test_inline_exception_case_is_collected(monkeypatch) -> None:
    monkeypatch.setattr(niltest._config, "_MODE", "test")

    @scenario("parse")
    def parse(value: str) -> int:
        if expect:
            expect.case("invalid", given={"value": "x"}, raises=ValueError)
        return int(value)

    assert niltest.run_tests(parse).success


def test_exception_case_reports_missing_wrong_and_message_mismatch(monkeypatch) -> None:
    monkeypatch.setattr(niltest._config, "_MODE", "test")

    @scenario("broken exceptions")
    @docs(
        case("missing", given={"kind": "none"}, raises=ValueError),
        case("wrong", given={"kind": "wrong"}, raises=ValueError),
        case("message", given={"kind": "message"}, raises=ValueError, match="wanted"),
    )
    def operation(kind: str) -> str:
        if kind == "wrong":
            raise TypeError("wrong type")
        if kind == "message":
            raise ValueError("other message")
        return "ok"

    results = niltest.run_tests(operation).scenarios[0].cases
    assert [result.status for result in results] == ["failed", "failed", "failed"]
    assert "but returned" in results[0].reason
    assert "but raised TypeError" in results[1].reason
    assert "did not match" in results[2].reason


def test_exception_case_never_acts_as_a_mock(monkeypatch) -> None:
    monkeypatch.setattr(niltest._config, "_MODE", "mock")

    @scenario("mock safety")
    @docs(case("failure", given={"value": -1}, raises=ValueError))
    def validate(value: int) -> int:
        raise ValueError("real implementation")

    try:
        validate(-1)
    except ValueError as error:
        assert str(error) == "real implementation"
    else:
        raise AssertionError("the real exception was not raised")


def test_case_requires_exactly_one_expectation() -> None:
    try:
        case("missing", given={})
    except ValueError as error:
        assert "exactly one" in str(error)
    else:
        raise AssertionError("missing expectation was accepted")

    try:
        case("both", given={}, returns=1, raises=ValueError)
    except ValueError as error:
        assert "exactly one" in str(error)
    else:
        raise AssertionError("two expectations were accepted")

    try:
        case("regex", given={}, raises=ValueError, match="[")
    except ValueError as error:
        assert "invalid exception match pattern" in str(error)
    else:
        raise AssertionError("invalid exception regex was accepted")


def test_async_exception_case(monkeypatch) -> None:
    monkeypatch.setattr(niltest._config, "_MODE", "test")

    @scenario("async failure")
    @docs(case("invalid", given={"value": -1}, raises=ValueError))
    async def validate(value: int) -> int:
        if value < 0:
            raise ValueError("negative")
        return value

    assert niltest.run_tests(validate).success
