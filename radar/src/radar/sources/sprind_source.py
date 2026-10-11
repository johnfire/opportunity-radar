"""SPRIND: the challenge cards on sprind.org. A card badged 'Apply now' is an open call."""

import html
import re
from datetime import date

from radar.http_transport import HttpRequest, SourceFetchError, Transport
from radar.opportunity_model import Opportunity, RunContext
from radar.plain_text_extraction import extract_plain_text

SOURCE_NAME = "sprind"
SITE_ROOT = "https://www.sprind.org"
CHALLENGES_URL = SITE_ROOT + "/en/challenges/"
_CARD_LINK_PATTERN = re.compile(r'<a href="(/en/actions/challenges/([a-z0-9.\-]+))"')
_TITLE_PATTERN = re.compile(r"<h3[^>]*>(.*?)</h3>", re.S)
_PARAGRAPH_PATTERN = re.compile(r"<p[^>]*>(.*?)</p>", re.S)
_DEADLINE_PATTERN = re.compile(r"(?:by|until|before)\s+([A-Z][a-z]+)\s+(\d{1,2})(?:,\s*(\d{4}))?")
_MONTHS = {
    name: number
    for number, name in enumerate(
        [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ],
        1,
    )
}


def _deadline_from_description(description: str, today: date) -> date | None:
    """Read 'Apply by November 16, 2026' or 'open until October 22'; with no year, the next such day."""
    match = _DEADLINE_PATTERN.search(description)
    if not match or match.group(1) not in _MONTHS:
        return None
    month, day = _MONTHS[match.group(1)], int(match.group(2))
    try:
        if match.group(3):
            return date(int(match.group(3)), month, day)
        this_year = date(today.year, month, day)
        return this_year if this_year >= today else date(today.year + 1, month, day)
    except ValueError:
        return None


def _card_texts(card_html: str) -> tuple[str, str]:
    titles, paragraphs = _TITLE_PATTERN.findall(card_html), _PARAGRAPH_PATTERN.findall(card_html)
    title = html.unescape(extract_plain_text(titles[-1])) if titles else ""
    description = html.unescape(extract_plain_text(paragraphs[-1])) if paragraphs else ""
    return title, description


def parse_sprind_challenges(page_html: str, today: date) -> list[Opportunity]:
    opportunities: list[Opportunity] = []
    card_start = 0
    for link in _CARD_LINK_PATTERN.finditer(page_html):
        card_html, card_start = page_html[card_start : link.end()], link.end()
        title, description = _card_texts(card_html)
        if "Apply now" not in card_html or not title:
            continue
        opportunities.append(
            Opportunity(
                source=SOURCE_NAME,
                source_id=link.group(2),
                title=title,
                buyer="SPRIND",
                url=SITE_ROOT + link.group(1),
                deadline=_deadline_from_description(description, today),
                amount_text=None,
                summary=description,
            )
        )
    return opportunities


def fetch_sprind_opportunities(transport: Transport, context: RunContext) -> list[Opportunity]:
    page_html = transport(HttpRequest(url=CHALLENGES_URL)).decode("utf-8", errors="replace")
    if not _CARD_LINK_PATTERN.search(page_html):
        raise SourceFetchError("SPRIND page has no challenge cards; the layout may have changed")
    return parse_sprind_challenges(page_html, context.today)
