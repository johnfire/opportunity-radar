"""BMFTR funding announcements: the ministry's list of Förderbekanntmachungen with a submission deadline."""

import re
from datetime import date, datetime
from html.parser import HTMLParser

from radar.http_transport import HttpRequest, SourceFetchError, Transport
from radar.opportunity_model import Opportunity, RunContext
from radar.plain_text_extraction import shorten_text

SOURCE_NAME = "bmftr"
LIST_URL = (
    "https://www.bmftr.bund.de/SiteGlobals/Forms/Suche/Bekanntmachungsuche/"
    "Bekanntmachungsuche_Formular.html?resultsPerPage=50&sortOrder=dateOfExpiration_dt+desc"
)
DEADLINE_COLUMN = 4
TITLE_COLUMN = 1
CATEGORY_COLUMN = 2
EXPECTED_COLUMNS = 5
TITLE_MAX_LENGTH = 200
_DATE_PATTERN = re.compile(r"^\d{2}\.\d{2}\.\d{4}$")


class _AnnouncementTableParser(HTMLParser):
    """Collects each table row as its cell texts plus the first link of the title cell."""

    def __init__(self) -> None:
        super().__init__()
        self.rows: list[tuple[list[str], str | None]] = []
        self._cells: list[str] | None = None
        self._cell_text: list[str] | None = None
        self._link: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self._cells, self._link = [], None
        elif tag == "td" and self._cells is not None:
            self._cell_text = []
        elif tag == "a" and self._cell_text is not None and self._link is None:
            self._link = dict(attrs).get("href")

    def handle_data(self, data: str) -> None:
        if self._cell_text is not None:
            self._cell_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "td" and self._cells is not None and self._cell_text is not None:
            self._cells.append(" ".join("".join(self._cell_text).split()))
            self._cell_text = None
        elif tag == "tr" and self._cells is not None:
            self.rows.append((self._cells, self._link))
            self._cells = None


def _parse_german_date(text: str) -> date | None:
    if not _DATE_PATTERN.match(text):
        return None
    return datetime.strptime(text, "%d.%m.%Y").date()


def parse_bmftr_announcements(page_html: str, today: date) -> list[Opportunity]:
    parser = _AnnouncementTableParser()
    parser.feed(page_html)
    opportunities: list[Opportunity] = []
    for cells, link in parser.rows:
        if len(cells) != EXPECTED_COLUMNS or not link:
            continue
        deadline = _parse_german_date(cells[DEADLINE_COLUMN])
        if deadline is None or deadline < today:
            continue
        opportunities.append(
            Opportunity(
                source=SOURCE_NAME,
                source_id=link.rsplit("/", 1)[-1].removesuffix(".html"),
                title=shorten_text(cells[TITLE_COLUMN], TITLE_MAX_LENGTH),
                buyer="BMFTR",
                url=link,
                deadline=deadline,
                amount_text=None,
                summary=cells[CATEGORY_COLUMN],
            )
        )
    return opportunities


def fetch_bmftr_opportunities(transport: Transport, context: RunContext) -> list[Opportunity]:
    page_html = transport(HttpRequest(url=LIST_URL)).decode("utf-8", errors="replace")
    if "<table" not in page_html:
        raise SourceFetchError("BMFTR answered without an announcements table")
    return parse_bmftr_announcements(page_html, context.today)
