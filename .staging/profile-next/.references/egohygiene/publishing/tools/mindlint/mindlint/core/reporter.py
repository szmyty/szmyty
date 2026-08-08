from __future__ import annotations

from collections import Counter

from rich.console import Console
from rich.text import Text

from mindlint.core.runner import ArticleLintResult, LintRunResult
from mindlint.models.issue import Issue


class RichReporter:
    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def report(self, result: LintRunResult) -> None:
        self.console.print("[bold]🧠 mindlint[/bold]")
        self.console.print()
        self.console.print(f"Found {result.article_count} articles.")
        self.console.print()

        for article_result in result.results:
            self._report_article(article_result)

        counts = Counter(issue.severity for issue in result.issues)
        passed = sum(1 for item in result.results if not item.issues)
        self.console.print()
        self.console.print("[bold]Summary:[/bold]")
        self.console.print(f"  passed: {passed}")
        self.console.print(f"  warnings: {counts['warning']}")
        self.console.print(f"  errors: {counts['error']}")

    def _report_article(self, result: ArticleLintResult) -> None:
        if not result.issues:
            self.console.print(f"✔ {result.article.path.name}")
            return

        marker = "❌" if result.has_errors else "⚠"
        self.console.print(f"{marker} {result.article.path.name}")
        for issue in result.issues:
            line = self._format_issue(issue)
            self.console.print(Text(f"  {line}"))

    def _format_issue(self, issue: Issue) -> str:
        location = f" (line {issue.line_number})" if issue.line_number is not None else ""
        suggestion = f" ({issue.suggestion})" if issue.suggestion else ""
        return (
            f"[{issue.severity}] {issue.rule_id}: "
            f"{issue.message}{location}{suggestion}"
        )
