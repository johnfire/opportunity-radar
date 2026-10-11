"""Turn HTML fragments into short plain text for digests."""

import html
import re

_TAG_PATTERN = re.compile(r"<[^>]+>")
_WHITESPACE_PATTERN = re.compile(r"\s+")


def extract_plain_text(html_fragment: str | None) -> str:
    if not html_fragment:
        return ""
    without_tags = _TAG_PATTERN.sub(" ", html_fragment)
    unescaped = html.unescape(without_tags).replace("\xa0", " ")
    return _WHITESPACE_PATTERN.sub(" ", unescaped).strip()


def shorten_text(text: str, max_length: int) -> str:
    if len(text) <= max_length:
        return text
    cut = text[: max_length - 1]
    last_space = cut.rfind(" ")
    if last_space > 0:
        cut = cut[:last_space]
    return cut.rstrip() + "…"
