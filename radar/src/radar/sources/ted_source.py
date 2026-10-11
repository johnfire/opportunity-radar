"""TED: EU-wide public tenders. Reads German contract notices in IT, software and R&D categories."""

import json
from datetime import date, timedelta
from typing import Any

from radar.http_transport import HttpRequest, SourceFetchError, Transport
from radar.opportunity_model import Opportunity, RunContext

SOURCE_NAME = "ted"
SEARCH_URL = "https://api.ted.europa.eu/v3/notices/search"
NOTICE_URL = "https://ted.europa.eu/en/notice/-/detail/{publication_number}"
# 72 = IT services, 73 = research and development services, 48 = software packages
CPV_PREFIXES = ("72*", "73*", "48*")
PAGE_SIZE = 100
MAX_PAGES = 5
LOOKBACK_DAYS = 120
REQUESTED_FIELDS = [
    "publication-number",
    "notice-title",
    "buyer-name",
    "deadline-receipt-tender-date-lot",
    "publication-date",
    "estimated-value-lot",
    "estimated-value-cur-lot",
]


def _localized_text(value: Any, preferred: tuple[str, ...] = ("deu", "eng")) -> str:
    if isinstance(value, dict):
        for language in preferred:
            if language in value:
                return _localized_text(value[language])
        return _localized_text(next(iter(value.values()), ""))
    if isinstance(value, list):
        return str(value[0]) if value else ""
    return str(value or "")


def _core_title(full_title: str) -> str:
    """TED titles read 'Country – Category – Subject'; only the subject helps in a digest."""
    segments = full_title.split(" – ", 2)
    return segments[2].strip() if len(segments) == 3 else full_title.strip()


def _earliest_future_deadline(deadlines: list[str], today: date) -> date | None:
    future = sorted(d for d in (date.fromisoformat(text[:10]) for text in deadlines) if d >= today)
    return future[0] if future else None


def _estimated_value_text(notice: dict[str, Any]) -> str | None:
    values = notice.get("estimated-value-lot") or []
    currencies = notice.get("estimated-value-cur-lot") or []
    if not values:
        return None
    try:
        amount = int(float(values[0]))
    except (TypeError, ValueError):
        return None
    currency = currencies[0] if currencies else "EUR"
    return f"geschätzt {amount:,} {currency}".replace(",", ".")


def _opportunity_from_notice(notice: dict[str, Any], deadline: date) -> Opportunity:
    publication_number = notice["publication-number"]
    full_title = _localized_text(notice.get("notice-title"))
    return Opportunity(
        source=SOURCE_NAME,
        source_id=publication_number,
        title=_core_title(full_title),
        buyer=_localized_text(notice.get("buyer-name")),
        url=NOTICE_URL.format(publication_number=publication_number),
        deadline=deadline,
        amount_text=_estimated_value_text(notice),
        summary=full_title,
    )


def parse_ted_notices(payload: dict[str, Any], today: date) -> list[Opportunity]:
    opportunities: list[Opportunity] = []
    for notice in payload["notices"]:
        deadline = _earliest_future_deadline(notice.get("deadline-receipt-tender-date-lot") or [], today)
        if deadline is not None:
            opportunities.append(_opportunity_from_notice(notice, deadline))
    return opportunities


def _search_request(cpv_prefix: str, page_number: int, today: date) -> HttpRequest:
    since = (today - timedelta(days=LOOKBACK_DAYS)).strftime("%Y%m%d")
    query = (
        f"buyer-country=DEU AND publication-date>={since} AND notice-type=cn-standard "
        f"AND deadline-receipt-tender-date-lot>={today.strftime('%Y%m%d')} "
        f"AND classification-cpv={cpv_prefix}"
    )
    body = {
        "query": query,
        "fields": REQUESTED_FIELDS,
        "limit": PAGE_SIZE,
        "page": page_number,
        "scope": "ALL",
        "paginationMode": "PAGE_NUMBER",
    }
    return HttpRequest(
        url=SEARCH_URL,
        method="POST",
        headers=(("Content-Type", "application/json"),),
        body=json.dumps(body).encode("utf-8"),
    )


def _read_page(transport: Transport, cpv_prefix: str, page_number: int, today: date) -> dict[str, Any]:
    raw = transport(_search_request(cpv_prefix, page_number, today))
    try:
        payload: dict[str, Any] = json.loads(raw)
        if not isinstance(payload["notices"], list):
            raise TypeError("notices is not a list")
    except (ValueError, KeyError, TypeError) as error:
        raise SourceFetchError(f"TED answered in an unexpected format ({error!r})") from error
    return payload


def fetch_ted_opportunities(transport: Transport, context: RunContext) -> list[Opportunity]:
    collected: dict[str, Opportunity] = {}
    for cpv_prefix in CPV_PREFIXES:
        for page_number in range(1, MAX_PAGES + 1):
            payload = _read_page(transport, cpv_prefix, page_number, context.today)
            for opportunity in parse_ted_notices(payload, context.today):
                collected.setdefault(opportunity.source_id, opportunity)
            if len(payload["notices"]) < PAGE_SIZE:
                break
    return list(collected.values())
