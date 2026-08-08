from __future__ import annotations

import emoji

from mindlint.models.article import Article
from mindlint.models.issue import Issue
from mindlint.rules.base import Rule


def has_emoji_prefix(text: str) -> bool:
    emojis = emoji.emoji_list(text)
    return bool(emojis and emojis[0]["match_start"] == 0)


class EmojiTitleRule(Rule):
    rule_id = "emoji-title"

    def check(self, article: Article) -> list[Issue]:
        if not article.title:
            return [
                Issue(
                    rule_id=self.rule_id,
                    severity="warning",
                    message="missing H1 title",
                    article_path=article.published_path,
                    suggestion="Add a top-level article title.",
                )
            ]

        if not has_emoji_prefix(article.title):
            return [
                Issue(
                    rule_id=self.rule_id,
                    severity="warning",
                    message="title should start with an emoji",
                    article_path=article.published_path,
                    line_number=1,
                    suggestion="Prefix the H1 with an article-relevant emoji.",
                )
            ]

        return []

