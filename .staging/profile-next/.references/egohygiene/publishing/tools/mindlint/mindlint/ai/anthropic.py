from __future__ import annotations

from mindlint.ai.base import AIProvider
from mindlint.models.article import Article
from mindlint.models.issue import Issue


class AnthropicProvider(AIProvider):
    def analyze_article(self, article: Article) -> list[Issue]:
        raise NotImplementedError(
            "AnthropicProvider is a paid-provider stub for a future implementation."
        )

