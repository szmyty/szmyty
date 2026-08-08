from __future__ import annotations

from abc import ABC, abstractmethod

from mindlint.models.article import Article
from mindlint.models.issue import Issue


class AIProvider(ABC):
    @abstractmethod
    def analyze_article(self, article: Article) -> list[Issue]:
        raise NotImplementedError

