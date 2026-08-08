from __future__ import annotations

import re
from pathlib import Path

import structlog

from mindlint.config.defaults import REQUIRED_FOOTER_DISCLOSURE, REQUIRED_IMAGE_DISCLOSURE
from mindlint.models.article import Article, ImageReference, RuleSuppression, Section

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
MEDIUM_ALT_RE = re.compile(r"<!--\s*ALT TEXT \(Medium\):.*?-->", re.IGNORECASE)
MEDIUM_ALT_LABEL_RE = re.compile(r"ALT TEXT \(Medium\):", re.IGNORECASE)
SUPPRESSION_RE = re.compile(
    r"<!--\s*mindlint-disable(?P<next>-next-line)?(?::|\s)?(?P<body>.*?)\s*-->",
    re.IGNORECASE,
)
SUPPRESSION_REASON_RE = re.compile(r"\s+(?:--|#)\s+", re.ASCII)
RULE_ID_RE = re.compile(r"[a-z0-9][a-z0-9-]*|\*", re.IGNORECASE)
log = structlog.get_logger(__name__)


def parse_article(article_dir: Path) -> Article:
    published_path = article_dir / "published.md"
    log.debug("parse_article.start", article_dir=str(article_dir), path=str(published_path))

    if not published_path.exists():
        log.debug("parse_article.missing_file", path=str(published_path))
        raise FileNotFoundError(f"{published_path} not found")

    text = published_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    sections = _extract_sections(lines)
    title = _extract_title(lines)
    images = _extract_images(lines)
    suppressions = _extract_suppressions(lines)
    has_table_of_contents = _has_section(sections, "Table of Contents")
    has_references = _has_section(sections, "References")
    has_footer_ai_disclosure = _has_footer_disclosure(text)

    log.debug(
        "parse_article.complete",
        article_dir=str(article_dir),
        title=title,
        line_count=len(lines),
        section_count=len(sections),
        image_count=len(images),
        suppression_count=len(suppressions),
        has_table_of_contents=has_table_of_contents,
        has_references=has_references,
        has_footer_ai_disclosure=has_footer_ai_disclosure,
    )

    return Article(
        path=article_dir,
        published_path=published_path,
        title=title,
        raw_text=text,
        sections=sections,
        images=images,
        suppressions=suppressions,
        has_table_of_contents=has_table_of_contents,
        has_references=has_references,
        has_footer_ai_disclosure=has_footer_ai_disclosure,
    )


def _extract_title(lines: list[str]) -> str:
    for index, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if match and len(match.group(1)) == 1:
            title = match.group(2).strip()
            log.debug("parser.title_found", line_number=index + 1, title=title)
            return title
    log.debug("parser.title_missing")
    return ""


def _extract_sections(lines: list[str]) -> list[Section]:
    heading_indexes: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if not match:
            continue

        level = len(match.group(1))
        if level in {2, 3}:
            title = match.group(2).strip()
            heading_indexes.append((index, level, title))
            log.debug(
                "parser.section_heading_found",
                line_number=index + 1,
                level=level,
                title=title,
            )

    sections: list[Section] = []
    for position, (line_index, level, title) in enumerate(heading_indexes):
        next_line_index = (
            heading_indexes[position + 1][0]
            if position + 1 < len(heading_indexes)
            else len(lines)
        )
        content = "\n".join(lines[line_index + 1 : next_line_index]).strip()
        sections.append(
            Section(
                level=level,
                title=title,
                content=content,
                line_number=line_index + 1,
            )
        )

    log.debug("parser.sections_extracted", count=len(sections))
    return sections


def _extract_images(lines: list[str]) -> list[ImageReference]:
    images: list[ImageReference] = []
    for index, line in enumerate(lines):
        for match in IMAGE_RE.finditer(line):
            caption = _find_caption(lines, index)
            has_medium_alt_comment = _has_nearby_alt_comment(lines, index)
            has_ai_caption_disclosure = _has_ai_disclosure(caption)
            image = ImageReference(
                alt_text=match.group(1).strip(),
                path=match.group(2).strip(),
                caption=caption,
                has_medium_alt_comment=has_medium_alt_comment,
                has_ai_caption_disclosure=has_ai_caption_disclosure,
                line_number=index + 1,
            )
            log.debug(
                "parser.image_found",
                line_number=image.line_number,
                alt_text=image.alt_text,
                path=image.path,
                caption=image.caption,
                has_medium_alt_comment=image.has_medium_alt_comment,
                has_ai_caption_disclosure=image.has_ai_caption_disclosure,
            )
            images.append(
                image
            )
    log.debug("parser.images_extracted", count=len(images))
    return images


def _extract_suppressions(lines: list[str]) -> list[RuleSuppression]:
    suppressions: list[RuleSuppression] = []
    for index, line in enumerate(lines):
        match = SUPPRESSION_RE.search(line)
        if not match:
            continue

        line_number = index + 1
        rule_ids, reason = _parse_suppression_body(match.group("body"))
        target_line_number = (
            _find_next_content_line(lines, index)
            if match.group("next")
            else None
        )
        suppression = RuleSuppression(
            rule_ids=frozenset(rule_ids),
            line_number=line_number,
            target_line_number=target_line_number,
            reason=reason,
        )
        suppressions.append(suppression)
        log.debug(
            "parser.suppression_found",
            line_number=line_number,
            target_line_number=target_line_number,
            rule_ids=sorted(suppression.rule_ids),
            reason=reason,
            scope="next-line" if target_line_number is not None else "file",
        )

    log.debug("parser.suppressions_extracted", count=len(suppressions))
    return suppressions


def _parse_suppression_body(body: str) -> tuple[set[str], str | None]:
    body = body.strip()
    if not body:
        return {"all"}, None

    parts = SUPPRESSION_REASON_RE.split(body, maxsplit=1)
    rule_text = parts[0]
    reason = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
    rule_ids = {match.group(0).lower() for match in RULE_ID_RE.finditer(rule_text)}
    if not rule_ids:
        rule_ids = {"all"}
    return rule_ids, reason


def _find_next_content_line(lines: list[str], suppression_line_index: int) -> int | None:
    for index in range(suppression_line_index + 1, len(lines)):
        candidate = lines[index].strip()
        if not candidate:
            continue
        if candidate.startswith("<!--") and candidate.endswith("-->"):
            continue
        return index + 1
    return None


def _find_caption(lines: list[str], image_line_index: int) -> str | None:
    in_comment = False
    caption_lines: list[str] = []

    for index in range(image_line_index + 1, min(image_line_index + 12, len(lines))):
        candidate = lines[index].strip()
        log.debug(
            "parser.caption_candidate",
            image_line_number=image_line_index + 1,
            candidate_line_number=index + 1,
            candidate=candidate,
            in_comment=in_comment,
        )

        if not candidate:
            if caption_lines:
                break
            continue

        # Handle multi-line comments
        if "<!--" in candidate:
            if "-->" not in candidate:
                in_comment = True
            log.debug(
                "parser.caption_skip_comment_start",
                image_line_number=image_line_index + 1,
                candidate_line_number=index + 1,
            )
            continue

        if "-->" in candidate:
            in_comment = False
            log.debug(
                "parser.caption_skip_comment_end",
                image_line_number=image_line_index + 1,
                candidate_line_number=index + 1,
            )
            continue

        if in_comment:
            log.debug(
                "parser.caption_skip_inside_comment",
                image_line_number=image_line_index + 1,
                candidate_line_number=index + 1,
            )
            continue

        # Skip headings and images
        if candidate.startswith("#") or IMAGE_RE.search(candidate) or candidate == "---":
            log.debug(
                "parser.caption_stopped_before_structure",
                image_line_number=image_line_index + 1,
                candidate_line_number=index + 1,
                candidate=candidate,
            )
            return None

        caption_lines.append(candidate)
        log.debug(
            "parser.caption_line_collected",
            image_line_number=image_line_index + 1,
            candidate_line_number=index + 1,
            candidate=candidate,
        )

    if caption_lines:
        caption = _strip_caption_markup("\n".join(caption_lines))
        log.debug(
            "parser.caption_found",
            image_line_number=image_line_index + 1,
            caption=caption,
        )
        return caption

    log.debug("parser.caption_missing", image_line_number=image_line_index + 1)
    return None


def _strip_caption_markup(text: str) -> str:
    text = text.strip()
    if text.startswith("*") and text.endswith("*"):
        return text.strip("*").strip()
    if text.startswith("_") and text.endswith("_"):
        return text.strip("_").strip()
    return text


def _has_nearby_alt_comment(lines: list[str], image_line_index: int) -> bool:
    start = max(0, image_line_index - 3)
    end = min(len(lines), image_line_index + 10)
    window = "\n".join(lines[start:end])
    has_alt_comment = bool(
        MEDIUM_ALT_RE.search(window)
        or ("<!--" in window and "-->" in window and MEDIUM_ALT_LABEL_RE.search(window))
    )
    log.debug(
        "parser.alt_comment_checked",
        image_line_number=image_line_index + 1,
        window_start_line=start + 1,
        window_end_line=end,
        has_alt_comment=has_alt_comment,
    )
    return has_alt_comment


def _has_section(sections: list[Section], expected_title: str) -> bool:
    return any(section.title.casefold() == expected_title.casefold() for section in sections)


def _has_footer_disclosure(text: str) -> bool:
    footer_region = text.strip()[-1000:]
    has_footer_disclosure = REQUIRED_FOOTER_DISCLOSURE in footer_region
    log.debug("parser.footer_disclosure_checked", found=has_footer_disclosure)
    return has_footer_disclosure


def _has_ai_disclosure(caption: str | None) -> bool:
    if not caption:
        log.debug("parser.ai_image_disclosure_checked", found=False, reason="no_caption")
        return False

    normalized = caption.lower()
    image_disclosure = REQUIRED_IMAGE_DISCLOSURE.lower()
    has_ai_disclosure = image_disclosure in normalized
    log.debug(
        "parser.ai_image_disclosure_checked",
        caption=caption,
        normalized_caption=normalized,
        required=image_disclosure,
        found=has_ai_disclosure,
    )
    return has_ai_disclosure
