from __future__ import annotations

from ._case import _Case
from ._compare import format_returns


def build_docstring(original_doc: str, title: str, cases: list[_Case]) -> str:
    """
    仕様ケース一覧から人間が読みやすいドックストリングを生成します。
    エディタ上でのホバー表示やhelp()の出力として使われます。
    """
    lines: list[str] = []

    if original_doc and original_doc.strip():
        lines.append(original_doc.strip())
        lines.append("")

    lines.append(f"Scenario: {title}")
    lines.append("=" * max(len(title) + 10, 40))

    for c in cases:
        lines.append(f"  [{c.name}]")
        if c.desc:
            lines.append(f"    説明    : {c.desc}")
        for k, v in c.given.items():
            lines.append(f"    {k:<10}: {v!r}")
        lines.append(f"    -> returns: {format_returns(c.returns)}")
        lines.append("")

    return "\n".join(lines)
