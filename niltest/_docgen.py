from __future__ import annotations

from . import _config
from ._case import _Case
from ._compare import format_returns
from ._i18n import translate


def build_docstring(original_doc: str, title: str, cases: list[_Case]) -> str:
    """
    仕様ケース一覧から人間が読みやすいドックストリングを生成します。
    エディタ上でのホバー表示やhelp()の出力として使われます。
    """
    lines: list[str] = []

    if original_doc and original_doc.strip():
        lines.append(original_doc.strip())
        lines.append("")

    lines.append(f"{translate(_config._LANGUAGE, 'scenario')}: {title}")
    lines.append("=" * max(len(title) + 10, 40))

    for c in cases:
        lines.append(f"  [{c.name}]")
        if c.desc:
            lines.append(f"    {translate(_config._LANGUAGE, 'description'):<10}: {c.desc}")
        for k, v in c.given.items():
            lines.append(f"    {k:<10}: {v!r}")
        if c.raises is None:
            label = translate(_config._LANGUAGE, "returns")
            expectation = format_returns(c.returns)
        else:
            label = translate(_config._LANGUAGE, "raises")
            exceptions = c.raises if isinstance(c.raises, tuple) else (c.raises,)
            expectation = " | ".join(exception.__name__ for exception in exceptions)
            if c.match is not None:
                expectation += f" ({c.match!r})"
        lines.append(f"    -> {label}: {expectation}")
        lines.append("")

    return "\n".join(lines)
