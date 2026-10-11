"""EU Funding & Tenders Portal: grants, calls and topics, read through the portal's public search service."""

import json
from datetime import date
from typing import Any

from radar.http_transport import HttpRequest, SourceFetchError, Transport
from radar.multipart_form_encoder import FormPart, encode_multipart_form
from radar.opportunity_model import Opportunity, RunContext
from radar.plain_text_extraction import shorten_text

SOURCE_NAME = "eu_portal"
BUYER_NAME = "EU Funding & Tenders Portal"
SEARCH_URL = "https://api.tech.ec.europa.eu/search-api/prod/rest/search"
PAGE_SIZE = 100
MAX_PAGES = 15
OPEN_OR_FORTHCOMING_QUERY = {
    "bool": {
        "must": [
            {"terms": {"type": ["1", "2", "8"]}},
            {"terms": {"status": ["31094501", "31094502"]}},
        ]
    }
}


def _first(metadata: dict[str, Any], field: str) -> str | None:
    value = metadata.get(field)
    if isinstance(value, list):
        return str(value[0]) if value else None
    return str(value) if value is not None else None


def _deadline_from(metadata: dict[str, Any]) -> date | None:
    text = _first(metadata, "deadlineDate")
    return date.fromisoformat(text[:10]) if text else None


def _format_budget(budget_text: str | None) -> str | None:
    if not budget_text:
        return None
    try:
        amount = int(float(budget_text))
    except ValueError:
        return None
    return f"Budget laut Portal: {amount:,} €".replace(",", ".")


def _opportunity_from_metadata(metadata: dict[str, Any], deadline: date) -> Opportunity:
    identifier = _first(metadata, "identifier") or ""
    title = _first(metadata, "title") or identifier
    return Opportunity(
        source=SOURCE_NAME,
        source_id=identifier,
        title=title,
        buyer=BUYER_NAME,
        url=_first(metadata, "url") or "",
        deadline=deadline,
        amount_text=_format_budget(_first(metadata, "budget")),
        summary=shorten_text(_first(metadata, "callTitle") or "", 300),
    )


def parse_eu_portal_results(payload: dict[str, Any], today: date) -> list[Opportunity]:
    opportunities: list[Opportunity] = []
    for result in payload["results"]:
        metadata = result["metadata"]
        deadline = _deadline_from(metadata)
        if deadline is not None and deadline >= today:
            opportunities.append(_opportunity_from_metadata(metadata, deadline))
    return opportunities


# Without an explicit sort the portal orders by relevance and pages overlap, which silently drops topics.
STABLE_SORT = {"field": "deadlineDate", "order": "ASC"}


def _page_request(page_number: int) -> HttpRequest:
    parts = [
        FormPart("query", json.dumps(OPEN_OR_FORTHCOMING_QUERY), "application/json"),
        FormPart("languages", '["en"]', "application/json"),
        FormPart("sort", json.dumps(STABLE_SORT), "application/json"),
    ]
    content_type, body = encode_multipart_form(parts)
    url = f"{SEARCH_URL}?apiKey=SEDIA&text=***&pageSize={PAGE_SIZE}&pageNumber={page_number}"
    return HttpRequest(url=url, method="POST", headers=(("Content-Type", content_type),), body=body)


def _read_page(transport: Transport, page_number: int) -> dict[str, Any]:
    raw = transport(_page_request(page_number))
    try:
        payload: dict[str, Any] = json.loads(raw)
        payload["results"]
        payload["totalResults"]
    except (ValueError, KeyError, TypeError) as error:
        raise SourceFetchError(
            f"EU Funding & Tenders Portal answered in an unexpected format ({error!r})"
        ) from error
    return payload


def fetch_eu_portal_opportunities(transport: Transport, context: RunContext) -> list[Opportunity]:
    collected: dict[str, Opportunity] = {}
    for page_number in range(1, MAX_PAGES + 1):
        payload = _read_page(transport, page_number)
        for opportunity in parse_eu_portal_results(payload, context.today):
            collected.setdefault(opportunity.source_id, opportunity)
        if page_number * PAGE_SIZE >= payload["totalResults"]:
            break
    return list(collected.values())
