from __future__ import annotations

import importlib
import inspect
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

import pytest
from _pytest._code.code import TerminalRepr

if TYPE_CHECKING:
    from niltest._case import _Case
    from niltest._result import CaseResult


class NiltestFailure(AssertionError):
    """A specification failure rendered by pytest without an internal traceback."""

    def __init__(self, result: CaseResult) -> None:
        super().__init__(result.reason)
        self.result = result


class NiltestItem(pytest.Item):
    def __init__(self, *, target: Any, case: _Case, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.target = target
        self.case = case
        self.result: CaseResult | None = None
        self.user_properties.extend(
            [
                ("niltest.scenario", getattr(target, "__niltest_title__", "")),
                ("niltest.case", case.name),
                ("niltest.source", case.source),
            ]
        )

    def runtest(self) -> None:
        runner = self.target.__niltest_run_case__
        self.result = runner(self.case)
        if not self.result.passed:
            raise NiltestFailure(self.result)

    def repr_failure(
        self,
        excinfo: pytest.ExceptionInfo[BaseException],
        style: Literal["long", "short", "line", "no", "native", "value", "auto"] | None = None,
    ) -> str | TerminalRepr:
        if isinstance(excinfo.value, NiltestFailure):
            return _format_failure(excinfo.value.result)
        return super().repr_failure(excinfo, style=style)

    def reportinfo(self) -> tuple[Path, int, str]:
        source_file = self.case.source_file or inspect.getsourcefile(self.target) or "niltest"
        return Path(source_file), max(self.case.source_line - 1, 0), f"niltest: {self.name}"


def _format_failure(result: CaseResult) -> str:
    lines = [
        f"niltest specification failed: {result.scenario} / {result.name}",
        f"function: {result.function}",
        f"given: {result.given!r}",
        f"expected: {result.expected}",
        f"actual: {result.actual or '<not produced>'}",
    ]
    if result.source:
        lines.append(f"source: {result.source}")
    if result.reason:
        lines.extend(["", result.reason])
    return "\n".join(lines)


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("niltest")
    group.addoption(
        "--niltest",
        action="store_true",
        default=False,
        help="collect registered niltest specification cases as pytest items",
    )
    group.addoption(
        "--niltest-module",
        action="append",
        default=[],
        metavar="MODULE",
        help="import a module containing niltest scenarios (repeatable)",
    )
    parser.addini(
        "niltest_modules",
        "modules imported when --niltest is enabled",
        type="linelist",
    )


def pytest_configure(config: pytest.Config) -> None:
    if config.getoption("--niltest"):
        from niltest import _config

        # This hook runs before test-module collection, so decorators see test mode.
        _config._MODE = "test"


def pytest_sessionstart(session: pytest.Session) -> None:
    config = session.config
    if not config.getoption("--niltest"):
        return
    modules = [*config.getini("niltest_modules"), *config.getoption("--niltest-module")]
    for module in dict.fromkeys(modules):
        try:
            importlib.import_module(module)
        except Exception as error:
            raise pytest.UsageError(f"niltest could not import {module!r}: {error}") from error


def pytest_collection_modifyitems(
    session: pytest.Session,
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    if not config.getoption("--niltest"):
        return

    from niltest._scenario import _registry

    niltest_items: list[pytest.Item] = []
    for target in _registry.values():
        get_cases = getattr(target, "__niltest_get_cases__", None)
        if get_cases is None:
            continue
        title = getattr(target, "__niltest_title__", target.__name__)
        for case in get_cases():
            niltest_items.append(
                NiltestItem.from_parent(
                    session,
                    name=f"{title}::{case.name}",
                    target=target,
                    case=case,
                )
            )
    items.extend(niltest_items)
