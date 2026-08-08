from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuleSuppression:
    rule_ids: frozenset[str]
    line_number: int
    target_line_number: int | None = None
    reason: str | None = None

    @property
    def is_file_level(self) -> bool:
        return self.target_line_number is None

    def matches(self, rule_id: str, issue_line_number: int | None) -> bool:
        if not _rule_matches(self.rule_ids, rule_id):
            return False
        if self.is_file_level:
            return True
        return issue_line_number == self.target_line_number


@dataclass(frozen=True)
class Section:
    level: int
    title: str
    content: str
    line_number: int | None = None


@dataclass(frozen=True)
class ImageReference:
    alt_text: str
    path: str
    caption: str | None
    has_medium_alt_comment: bool
    has_ai_caption_disclosure: bool
    line_number: int | None = None


@dataclass(frozen=True)
class Article:
    path: Path
    published_path: Path
    title: str
    raw_text: str
    sections: list[Section]
    images: list[ImageReference]
    suppressions: list[RuleSuppression]
    has_table_of_contents: bool
    has_references: bool
    has_footer_ai_disclosure: bool


def _rule_matches(rule_ids: frozenset[str], rule_id: str) -> bool:
    return not rule_ids or "*" in rule_ids or "all" in rule_ids or rule_id in rule_ids
