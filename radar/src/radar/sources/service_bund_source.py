"""service.bund.de: federal tender notices, searched once per topic word and merged."""

import html
import re
from datetime import date, datetime
from urllib.parse import quote

from radar.http_transport import HttpRequest, SourceFetchError, Transport
from radar.opportunity_model import Opportunity, RunContext
from radar.plain_text_extraction import extract_plain_text

SOURCE_NAME = "service_bund"
SITE_ROOT = "https://www.service.bund.de/"
SEARCH_URL = (
    SITE_ROOT + "Content/DE/Ausschreibungen/Suche/Formular.html"
    "?nn=4641514&resultsPerPage=100&templateQueryString={term}"
)
SEARCH_TERMS = (
    "Software",
    "Softwareentwicklung",
    "Künstliche Intelligenz",
    "Daten",
    "Digitalisierung",
    "App",
    "Plattform",
    "Datenanalyse",
)
_SOFT_HYPHEN = "­"
_RESULT_PATTERN = re.compile(r"<li>\s*<a href=\"([^\"]+)\".*?</li>", re.S)
_TITLE_PATTERN = re.compile(r"<h3><em>[^<]*</em>(.*?)</h3>", re.S)
_BUYER_PATTERN = re.compile(r"<em>Vergabestelle</em>(.*?)</p>", re.S)
_DEADLINE_PATTERN = re.compile(r"<em>Angebotsfrist</em>\s*(\d{2}\.\d{2}\.\d{2})")


def _clean_link(href: str) -> str:
    """Drop the session id and query string so the same notice always gets the same address."""
    path = href.split(";", 1)[0].split("?", 1)[0]
    return SITE_ROOT + path


def _opportunity_from_result(block: str, href: str, today: date) -> Opportunity | None:
    title_match, deadline_match = _TITLE_PATTERN.search(block), _DEADLINE_PATTERN.search(block)
    if not title_match or not deadline_match:
        return None
    deadline = datetime.strptime(deadline_match.group(1), "%d.%m.%y").date()
    if deadline < today:
        return None
    link = _clean_link(href)
    buyer_match = _BUYER_PATTERN.search(block)
    return Opportunity(
        source=SOURCE_NAME,
        source_id=link.rsplit("/", 1)[-1].removesuffix(".html"),
        title=html.unescape(extract_plain_text(title_match.group(1))).replace(_SOFT_HYPHEN, ""),
        buyer=html.unescape(extract_plain_text(buyer_match.group(1))) if buyer_match else "",
        url=link,
        deadline=deadline,
        amount_text=None,
        summary="",
    )


def parse_service_bund_results(page_html: str, today: date) -> list[Opportunity]:
    parsed = (
        _opportunity_from_result(m.group(0), m.group(1), today) for m in _RESULT_PATTERN.finditer(page_html)
    )
    return [opportunity for opportunity in parsed if opportunity is not None]


def fetch_service_bund_opportunities(transport: Transport, context: RunContext) -> list[Opportunity]:
    collected: dict[str, Opportunity] = {}
    for term in SEARCH_TERMS:
        page_html = transport(HttpRequest(url=SEARCH_URL.format(term=quote(term)))).decode(
            "utf-8", errors="replace"
        )
        if 'class="result-list"' not in page_html and "Keine Treffer" not in page_html:
            raise SourceFetchError(
                f"service.bund.de answered the search for {term!r} in an unexpected format"
            )
        for opportunity in parse_service_bund_results(page_html, context.today):
            collected.setdefault(opportunity.source_id, opportunity)
    return list(collected.values())
