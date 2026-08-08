from __future__ import annotations

from mindlint.models.article import Article, Section
from mindlint.models.issue import Issue
from mindlint.rules.base import Rule


class TableOfContentsRule(Rule):
    rule_id = "table-of-contents"

    def check(self, article: Article) -> list[Issue]:
        toc = _find_section(article.sections, "Table of Contents")
        if toc is None:
            return [
                Issue(
                    rule_id=self.rule_id,
                    severity="warning",
                    message="missing Table of Contents section",
                    article_path=article.published_path,
                    suggestion="Add a ## Table of Contents section before Introduction.",
                )
            ]

        introduction = _find_section(article.sections, "Introduction")
        if introduction is not None and toc.line_number and introduction.line_number:
            if toc.line_number > introduction.line_number:
                return [
                    Issue(
                        rule_id=self.rule_id,
                        severity="warning",
                        message="Table of Contents should appear before Introduction",
                        article_path=article.published_path,
                        line_number=toc.line_number,
                    )
                ]

        if article.images and toc.line_number and article.images[0].line_number:
            first_image_line = article.images[0].line_number
            if toc.line_number <= first_image_line:
                return [
                    Issue(
                        rule_id=self.rule_id,
                        severity="warning",
                        message="Table of Contents should appear after the header image",
                        article_path=article.published_path,
                        line_number=toc.line_number,
                    )
                ]

        return []


def _find_section(sections: list[Section], title: str) -> Section | None:
    for section in sections:
        if section.title.casefold() == title.casefold():
            return section
    return None

