from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class CaseResult:
    """Result of one executable specification case."""

    name: str
    status: str
    reason: str = ""

    @property
    def passed(self) -> bool:
        return self.status == "passed"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ScenarioResult:
    """Results produced by one scenario."""

    title: str
    cases: tuple[CaseResult, ...] = field(default_factory=tuple)

    @property
    def passed(self) -> int:
        return sum(case.passed for case in self.cases)

    @property
    def failed(self) -> int:
        return len(self.cases) - self.passed

    @property
    def success(self) -> bool:
        return bool(self.cases) and self.failed == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "passed": self.passed,
            "failed": self.failed,
            "success": self.success,
            "cases": [case.to_dict() for case in self.cases],
        }


@dataclass(frozen=True)
class RunResult:
    """Aggregate result returned by :func:`niltest.run_tests`."""

    scenarios: tuple[ScenarioResult, ...] = field(default_factory=tuple)

    @property
    def passed(self) -> int:
        return sum(scenario.passed for scenario in self.scenarios)

    @property
    def failed(self) -> int:
        return sum(scenario.failed for scenario in self.scenarios)

    @property
    def success(self) -> bool:
        return bool(self.scenarios) and all(scenario.success for scenario in self.scenarios)

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "failed": self.failed,
            "success": self.success,
            "scenarios": [scenario.to_dict() for scenario in self.scenarios],
        }
