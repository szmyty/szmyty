from __future__ import annotations

from mindlint.models.article import Article
from mindlint.models.issue import Issue
from mindlint.rules.base import Rule


class FooterAIDisclosureRule(Rule):
    rule_id = "footer-ai-disclosure"

    def check(self, article: Article) -> list[Issue]:
        if article.has_footer_ai_disclosure:
            return []

        return [
            Issue(
                rule_id=self.rule_id,
                severity="error",
                message="missing footer AI disclosure at bottom of article",
                article_path=article.published_path,
                suggestion="Add the required AI disclosure as the final text.",
            )
        ]

