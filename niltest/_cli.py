from __future__ import annotations

import argparse
import importlib
import io
import json
import sys
from collections.abc import Sequence
from contextlib import redirect_stdout
from typing import Any

from . import __version__, configure, run_tests
from ._inspect import format_inspection, format_markdown, inspect_scenarios
from ._scenario import _registry


def _configure_utf8_stream(stream: Any) -> None:
    """Use UTF-8 for CLI output when the host selected a legacy encoding."""
    encoding = str(getattr(stream, "encoding", "")).lower().replace("-", "")
    if encoding in {"utf8", "utf8sig"}:
        return
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is None:
        return
    try:
        reconfigure(encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        # Captured or embedded streams may expose reconfigure but reject it.
        pass


def _configure_output_encoding() -> None:
    _configure_utf8_stream(sys.stdout)
    _configure_utf8_stream(sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="niltest",
        description="Run executable specifications embedded in Python functions.",
    )
    parser.add_argument("--version", action="version", version=f"niltest {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", help="Import modules and run their registered scenarios")
    run.add_argument("modules", nargs="+", help="Import path, for example: myapp.specs")
    run.add_argument("--language", "-l", help="Output locale, for example: en or ja")
    run.add_argument("--json", action="store_true", help="Print a machine-readable summary")
    inspect_command = subparsers.add_parser(
        "inspect", help="Show signatures, types, cases, and input diagnostics"
    )
    inspect_command.add_argument("modules", nargs="+", help="Import path to inspect")
    inspect_command.add_argument("--language", "-l", help="Output locale")
    inspect_command.add_argument(
        "--format",
        choices=("text", "json", "markdown"),
        default="text",
        help="Output format (default: text)",
    )
    inspect_command.add_argument(
        "--json", action="store_true", help="Deprecated alias for --format json"
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    _configure_output_encoding()
    args = build_parser().parse_args(argv)
    if args.language:
        configure(language=args.language)
    configure(mode="test")

    try:
        for module in args.modules:
            importlib.import_module(module)
    except Exception as error:
        print(f"niltest: could not import '{module}': {error}", file=sys.stderr)
        return 2

    requested = set(args.modules)
    targets = [
        target for target in _registry.values() if getattr(target, "__module__", "") in requested
    ]
    if not targets:
        print("niltest: imported modules did not register any scenarios", file=sys.stderr)
        return 2
    if args.command == "inspect":
        report = inspect_scenarios(targets)
        output_format = "json" if args.json else args.format
        if output_format == "json":
            print(json.dumps(report, ensure_ascii=False, indent=2, default=repr))
        elif output_format == "markdown":
            print(format_markdown(report), end="")
        else:
            print(format_inspection(report))
        return 0 if report["valid"] else 1

    if args.json:
        with redirect_stdout(io.StringIO()):
            result = run_tests(*targets)
    else:
        result = run_tests(*targets)
    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
