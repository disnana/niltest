from __future__ import annotations

import json

import niltest
from niltest._cli import main


def test_run_tests_returns_machine_readable_result():
    from niltest import expect, scenario

    niltest.configure(production=False, mode="MOCK", language="en")

    @scenario("Double")
    def double(value: int) -> int:
        if expect:
            expect.case("two", given={"value": 2}, returns=4)
        return value * 2

    result = niltest.run_tests(double)
    assert result.success
    assert result.passed == 1
    assert result.failed == 0
    assert result.to_dict()["scenarios"][0]["cases"][0]["status"] == "passed"


def test_cli_runs_demo_and_emits_json(capsys):
    exit_code = main(["run", "examples.demo", "--language", "en", "--json"])
    output = capsys.readouterr().out
    payload = json.loads(output)
    assert exit_code == 0
    assert payload["success"] is True
    assert payload["passed"] == 3


def test_cli_returns_two_for_import_error(capsys):
    assert main(["run", "module_that_does_not_exist"]) == 2
    assert "could not import" in capsys.readouterr().err
