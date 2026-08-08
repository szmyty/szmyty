from __future__ import annotations

from pathlib import Path

from mindlint.models.article import Article, ImageReference
from mindlint.models.issue import Issue
from mindlint.rules.base import Rule


class VisualsRule(Rule):
    rule_id = "visuals"

    def check(self, article: Article) -> list[Issue]:
        issues: list[Issue] = []
        for position, image in enumerate(article.images, start=1):
            label = _image_label(position, image)
            if image.caption is None:
                issues.append(
                    Issue(
                        rule_id=self.rule_id,
                        severity="error",
                        message=f"{label} missing caption",
                        article_path=article.published_path,
                        line_number=image.line_number,
                    )
                )
            elif not image.has_ai_caption_disclosure:
                issues.append(
                    Issue(
                        rule_id=self.rule_id,
                        severity="error",
                        message=f"{label} missing AI image disclosure",
                        article_path=article.published_path,
                        line_number=image.line_number,
                        suggestion="Add 'This image was generated using AI.' to the caption.",
                    )
                )

            if not image.has_medium_alt_comment:
                issues.append(
                    Issue(
                        rule_id=self.rule_id,
                        severity="warning",
                        message=f"{label} missing Medium alt text comment",
                        article_path=article.published_path,
                        line_number=image.line_number,
                    )
                )

            if _is_local_image(image.path) and not (article.path / image.path).exists():
                issues.append(
                    Issue(
                        rule_id=self.rule_id,
                        severity="warning",
                        message=f"{label} image file does not exist locally",
                        article_path=article.published_path,
                        line_number=image.line_number,
                    )
                )

        return issues


def _image_label(position: int, image: ImageReference) -> str:
    if image.alt_text:
        return image.alt_text
    return f"figure{position}"


def _is_local_image(path: str) -> bool:
    return not (
        path.startswith("http://")
        or path.startswith("https://")
        or path.startswith("#")
        or Path(path).is_absolute()
    )

