from __future__ import annotations

import json
from typing import Annotated

import pytest

import niltest
from niltest._cli import main


class PayloadForInputConversion(pytest.importorskip("pydantic").BaseModel):
    count: int


class ConstrainedPayloadForInputValidation(pytest.importorskip("pydantic").BaseModel):
    count: Annotated[int, pytest.importorskip("pydantic").Field(gt=0)]


@pytest.fixture(autouse=True)
def reset_mode_and_registry():
    import niltest._config as config
    from niltest._scenario import _registry

    previous_mode = config._MODE
    config._MODE = "test"
    _registry.clear()
    yield
    _registry.clear()
    config._MODE = previous_mode


def test_conforms_to_accepts_pydantic_compatible_types() -> None:
    pydantic = pytest.importorskip("pydantic")

    class User(pydantic.BaseModel):
        id: int
        name: str

    positive = Annotated[int, pydantic.Field(gt=0)]
    from niltest._compare import returns_match

    assert returns_match({"id": 1, "name": "Alice"}, niltest.conforms_to(User))[0]
    assert returns_match([1, 2], niltest.conforms_to(list[positive]))[0]
    matched, reason = returns_match([0], niltest.conforms_to(list[positive]))
    assert not matched
    assert "type validation failed" in reason


def test_conforms_to_is_not_used_as_a_mock() -> None:
    from niltest import case, conforms_to, docs, scenario

    @scenario("typed result")
    @docs(case("positive", given={"value": 2}, returns=conforms_to(int)))
    def double(value: int) -> int:
        return value * 2

    niltest.configure(mode="mock")
    assert double(2) == 4
    assert niltest.run_tests(double).success


def test_invalid_case_input_is_reported_before_execution() -> None:
    from niltest import case, docs, scenario

    calls = 0

    @scenario("validated input")
    @docs(case("invalid", given={"payload": {"count": 0}}, returns=1))
    def process(payload: ConstrainedPayloadForInputValidation) -> int:
        nonlocal calls
        calls += 1
        return payload.count

    result = niltest.run_tests(process)
    assert not result.success
    assert result.scenarios[0].cases[0].status == "error"
    assert "payload" in result.scenarios[0].cases[0].reason
    assert calls == 0


def test_valid_case_input_is_converted_to_a_pydantic_model() -> None:
    from niltest import case, docs, scenario

    @scenario("normalized input")
    @docs(case("dict input", given={"payload": {"count": 2}}, returns=4))
    def process(payload: PayloadForInputConversion) -> int:
        return payload.count * 2

    assert niltest.run_tests(process).success


def test_input_normalization_does_not_change_normal_calls() -> None:
    from niltest import case, docs, scenario

    @scenario("normal calls remain plain Python")
    @docs(case("dict input", given={"payload": {"count": 2}}, returns=4))
    def process(payload: PayloadForInputConversion) -> int:
        return payload.count * 2

    niltest.configure(mode="test")
    with pytest.raises(AttributeError):
        process({"count": 2})  # type: ignore[arg-type]


def test_conforms_to_strict_rejects_coercion() -> None:
    from niltest._compare import returns_match

    assert returns_match("1", niltest.conforms_to(int))[0]
    matched, reason = returns_match("1", niltest.conforms_to(int, strict=True))
    assert not matched
    assert "type validation failed" in reason


def test_missing_and_unknown_case_arguments_are_reported() -> None:
    from niltest._typing import validate_case_inputs

    def target(required: int) -> None:
        pass

    assert "missing" in validate_case_inputs(target, ({}))[0]
    assert "unexpected" in validate_case_inputs(target, {"required": 1, "other": 1})[0]


def test_inspect_cli_emits_json_for_typed_scenarios(tmp_path, monkeypatch, capsys) -> None:
    module = tmp_path / "inspect_example.py"
    module.write_text(
        "from niltest import case, conforms_to, docs, scenario\n"
        "@scenario('Lookup')\n"
        "@docs(case('one', given={'value': 1}, returns=conforms_to(int)))\n"
        "def lookup(value: int) -> int:\n"
        "    return value\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    exit_code = main(["inspect", "inspect_example", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert payload["scenario_count"] == 1
    scenario = payload["scenarios"][0]
    assert scenario["returns"] == "int"
    assert scenario["signature"] == "lookup(value: int) -> int"
    assert scenario["parameters"] == [{"name": "value", "type": "int", "required": True}]
    assert scenario["untyped_parameters"] == []
    assert scenario["mockable_cases"] == 0
    assert scenario["cases"][0]["returns"] == "conforms_to(int)"


def test_inspect_cli_reports_invalid_cases(tmp_path, monkeypatch, capsys) -> None:
    module = tmp_path / "invalid_inspect_example.py"
    module.write_text(
        "from niltest import case, docs, scenario\n"
        "@scenario('Broken')\n"
        "@docs(case('missing input', given={}, returns=1))\n"
        "def lookup(value: int) -> int:\n"
        "    return value\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    exit_code = main(["inspect", "invalid_inspect_example", "--language", "en"])
    output = capsys.readouterr().out
    assert exit_code == 1
    assert "[INVALID] missing input" in output
    assert "missing" in output


def test_inspect_cli_localizes_human_output(tmp_path, monkeypatch, capsys) -> None:
    module = tmp_path / "localized_inspect_example.py"
    module.write_text(
        "from niltest import case, docs, scenario\n"
        "@scenario('検索')\n"
        "@docs(case('一件', given={'value': 1}, returns=1))\n"
        "def lookup(value: int) -> int:\n"
        "    return value\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    exit_code = main(["inspect", "localized_inspect_example", "--language", "ja"])
    output = capsys.readouterr().out
    assert exit_code == 0
    assert "シナリオ: 検索" in output
    assert "戻り値: int" in output
    assert "ケース: 1 (モック可能: 1)" in output
