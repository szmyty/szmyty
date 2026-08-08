from __future__ import annotations

from abc import ABC, abstractmethod

from mindlint.models.article import Article
from mindlint.models.issue import Issue


class Rule(ABC):
    rule_id: str

    @abstractmethod
    def check(self, article: Article) -> list[Issue]:
        raise NotImplementedError

