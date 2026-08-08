from __future__ import annotations

import json
from typing import Any

import httpx
import structlog

from mindlint.ai.base import AIProvider
from mindlint.ai.prompts import build_quality_prompt
from mindlint.config.defaults import DEFAULT_OLLAMA_MODEL, DEFAULT_OLLAMA_URL
from mindlint.models.article import Article
from mindlint.models.issue import Issue

log = structlog.get_logger(__name__)


class OllamaProvider(AIProvider):
    rule_id = "ai-ollama"

    def __init__(
        self,
        model: str = DEFAULT_OLLAMA_MODEL,
        url: str = DEFAULT_OLLAMA_URL,
        timeout: float = 30.0,
    ) -> None:
        self.model = model
        self.url = url
        self.timeout = timeout

    def analyze_article(self, article: Article) -> list[Issue]:
        log.debug(
            "ollama.analyze.start",
            article_path=str(article.published_path),
            model=self.model,
            url=self.url,
        )
        payload = {
            "model": self.model,
            "prompt": build_quality_prompt(article),
            "stream": False,
            "format": "json",
        }

        try:
            response = httpx.post(self.url, json=payload, timeout=self.timeout)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            log.debug(
                "ollama.analyze.unavailable",
                article_path=str(article.published_path),
                error=str(exc),
            )
            return [
                Issue(
                    rule_id=self.rule_id,
                    severity="warning",
                    message=f"Ollama analysis unavailable: {exc}",
                    article_path=article.published_path,
                )
            ]

        response_text = str(response.json().get("response", "")).strip()
        if not response_text:
            log.debug(
                "ollama.analyze.empty_response",
                article_path=str(article.published_path),
            )
            return []

        issues = _parse_ai_response(response_text, article)
        log.debug(
            "ollama.analyze.complete",
            article_path=str(article.published_path),
            issue_count=len(issues),
        )
        return issues


def _parse_ai_response(response_text: str, article: Article) -> list[Issue]:
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError:
        log.debug(
            "ollama.response_json_parse_failed",
            article_path=str(article.published_path),
            response_preview=response_text[:300],
        )
        return [
            Issue(
                rule_id=OllamaProvider.rule_id,
                severity="warning",
                message=response_text[:300],
                article_path=article.published_path,
            )
        ]

    raw_issues = data.get("issues", [])
    if not isinstance(raw_issues, list):
        log.debug(
            "ollama.response_issues_not_list",
            article_path=str(article.published_path),
        )
        return []

    issues: list[Issue] = []
    for raw_issue in raw_issues:
        if isinstance(raw_issue, str):
            message: str | None = raw_issue
            suggestion = None
        elif isinstance(raw_issue, dict):
            message = _string_value(raw_issue, "message")
            suggestion = _string_value(raw_issue, "suggestion")
        else:
            continue

        if not message:
            continue

        issues.append(
            Issue(
                rule_id=OllamaProvider.rule_id,
                severity="warning",
                message=message,
                article_path=article.published_path,
                suggestion=suggestion,
            )
        )

    return issues


def _string_value(data: dict[str, Any], key: str) -> str | None:
    value = data.get(key)
    return value if isinstance(value, str) and value.strip() else None
