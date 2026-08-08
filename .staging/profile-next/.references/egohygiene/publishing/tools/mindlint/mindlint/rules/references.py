from __future__ import annotations

import re

from mindlint.models.article import Article, Section
from mindlint.models.issue import Issue
from mindlint.rules.base import Rule

REFERENCE_ENTRY_RE = re.compile(r"^\s*(?:[-*]|\d+[.)])\s+\S+", re.MULTILINE)
REFERENCE_BLOCK_RE = re.compile(r"\(\d{4}[a-z]?\)|https?://|doi\.org/", re.IGNORECASE)


class ReferencesRule(Rule):
    rule_id = "references"

    def check(self, article: Article) -> list[Issue]:
        section = _find_references(article.sections)
        if section is None:
            return [
                Issue(
                    rule_id=self.rule_id,
                    severity="warning",
                    message="missing References section",
                    article_path=article.published_path,
                    suggestion="Add a ## References section with at least 3 entries.",
                )
            ]

        reference_count = _count_reference_entries(section.content)
        if reference_count < 3:
            return [
                Issue(
                    rule_id=self.rule_id,
                    severity="warning",
                    message=f"References section has {reference_count} reference-looking entries",
                    article_path=article.published_path,
                    line_number=section.line_number,
                    suggestion="Include at least 3 reference-looking entries.",
                )
            ]

        return []


def _find_references(sections: list[Section]) -> Section | None:
    for section in sections:
        if section.title.casefold() == "references":
            return section
    return None


def _count_reference_entries(content: str) -> int:
    bullet_entries = len(REFERENCE_ENTRY_RE.findall(content))
    paragraph_entries = sum(
        1
        for block in re.split(r"\n\s*\n", content)
        if REFERENCE_BLOCK_RE.search(block)
    )
    return max(bullet_entries, paragraph_entries)
