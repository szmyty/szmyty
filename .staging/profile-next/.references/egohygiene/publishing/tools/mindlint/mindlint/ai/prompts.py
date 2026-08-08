from __future__ import annotations

from mindlint.models.article import Article


def build_quality_prompt(article: Article) -> str:
    return f"""You are analyzing a Markdown article for qualitative writing issues.

Do not rewrite the article.
Do not generate new article content.
Only identify issues that are already present.
Return concise JSON if possible in this shape:
{{"issues":[{{"message":"...", "suggestion":"..."}}]}}

Check for:
- overly generic tone
- AI-like phrasing
- repetitive structure
- lack of authorial signal
- over-polished or emotionally flat sections

Title: {article.title}

Article:
{article.raw_text}
"""

