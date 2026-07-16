from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from niltest._scenario import _registry

pytest_plugins = ["pytester"]


@pytest.fixture(autouse=True)
def clear_registry(monkeypatch: pytest.MonkeyPatch) -> None:
    # pytester decodes subprocess output as UTF-8; force the same encoding on Windows.
    monkeypatch.setenv("PYTHONUTF8", "1")
    # Keep nested runs independent from whichever plugins happen to be installed.
    monkeypatch.setenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    _registry.clear()
    yield
    _registry.clear()


def test_pytest_plugin_collects_each_case(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        plugin_specs="""
        from niltest import case, docs, scenario

        @scenario("pricing")
        @docs(
            case("member", given={"member": True}, returns=90),
            case("guest", given={"member": False}, returns=100),
        )
        def price(member: bool) -> int:
            return 90 if member else 100
        """
    )
    pytester.syspathinsert(pytester.path)

    result = pytester.runpytest_subprocess(
        "-p",
        "niltest_pytest",
        "--niltest",
        "--niltest-module=plugin_specs",
        "-vv",
    )

    result.assert_outcomes(passed=2)
    result.stdout.fnmatch_lines(["*pricing::member*", "*pricing::guest*"])


def test_pytest_plugin_is_inert_without_flag(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        test_regular="""
        def test_regular():
            assert True
        """
    )
    pytester.syspathinsert(pytester.path)

    result = pytester.runpytest_subprocess("-p", "niltest_pytest", "-q")
    result.assert_outcomes(passed=1)


def test_pytest_plugin_imports_modules_from_configuration(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        configured_specs="""
        from niltest import case, docs, scenario

        @scenario("configured")
        @docs(case("one", given={"value": 1}, returns=1))
        def identity(value: int) -> int:
            return value
        """
    )
    pytester.makeini("[pytest]\nniltest_modules = configured_specs\n")
    pytester.syspathinsert(pytester.path)

    result = pytester.runpytest_subprocess("-p", "niltest_pytest", "--niltest", "-q")
    result.assert_outcomes(passed=1)


def test_pytest_failure_is_written_to_junit(pytester: pytest.Pytester) -> None:
    pytester.makepyfile(
        failing_specs="""
        from niltest import case, docs, scenario

        @scenario("calculation")
        @docs(case("wrong total", given={"value": 2}, returns=5))
        def double(value: int) -> int:
            return value * 2
        """
    )
    pytester.syspathinsert(pytester.path)
    report = pytester.path / "report.xml"

    result = pytester.runpytest_subprocess(
        "-p",
        "niltest_pytest",
        "--niltest",
        "--niltest-module=failing_specs",
        f"--junitxml={report}",
        "-q",
    )

    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(["*niltest specification failed: calculation / wrong total*"])
    root = ET.parse(report).getroot()
    test_case = root.find(".//testcase")
    assert test_case is not None
    assert test_case.attrib["name"] == "wrong total"
    assert "calculation" in test_case.attrib["classname"]
    failure = test_case.find("failure")
    assert failure is not None
    assert "expected: 5" in (failure.text or "")
