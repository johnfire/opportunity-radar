import copy
import json
from datetime import date
from typing import Any

import pytest

from radar.http_transport import HttpRequest, SourceFetchError
from radar.opportunity_model import RunContext
from radar.sources.eu_portal_source import (
    fetch_eu_portal_opportunities,
    parse_eu_portal_results,
)
from tests.conftest import RecordingTransport, load_fixture_json

TODAY = date(2026, 10, 11)
CONTEXT = RunContext(correlation_id="test-run", today=TODAY)


def test_topics_with_future_deadlines_are_kept() -> None:
    opportunities = parse_eu_portal_results(load_fixture_json("eu_portal_search.json"), TODAY)
    assert len(opportunities) == 6
    assert opportunities[0].source_id == "HORIZON-CL2-2027-01-TRANSFO-06"
    assert opportunities[0].deadline == date(2027, 9, 23)


def test_topics_with_past_deadlines_are_dropped() -> None:
    payload: Any = copy.deepcopy(load_fixture_json("eu_portal_search.json"))
    payload["results"][0]["metadata"]["deadlineDate"] = ["2026-09-01T00:00:00.000+0000"]
    opportunities = parse_eu_portal_results(payload, TODAY)
    assert "HORIZON-CL2-2027-01-TRANSFO-06" not in [o.source_id for o in opportunities]


def test_topics_without_deadline_are_dropped() -> None:
    payload: Any = copy.deepcopy(load_fixture_json("eu_portal_search.json"))
    del payload["results"][0]["metadata"]["deadlineDate"]
    opportunities = parse_eu_portal_results(payload, TODAY)
    assert len(opportunities) == 5


def test_fields_are_mapped_from_the_topic() -> None:
    first = parse_eu_portal_results(load_fixture_json("eu_portal_search.json"), TODAY)[0]
    assert first.source == "eu_portal"
    assert first.title.startswith("Closing the learning gap")
    assert first.url.startswith("https://ec.europa.eu/info/funding-tenders/")
    assert first.buyer == "EU Funding & Tenders Portal"


def test_budget_is_shown_when_the_portal_gives_one() -> None:
    payload: Any = copy.deepcopy(load_fixture_json("eu_portal_search.json"))
    payload["results"][0]["metadata"]["budget"] = ["2000000"]
    first = parse_eu_portal_results(payload, TODAY)[0]
    assert first.amount_text == "Budget laut Portal: 2.000.000 €"


def _page(total: int, identifiers: list[str]) -> bytes:
    base: Any = copy.deepcopy(load_fixture_json("eu_portal_search.json"))
    template = base["results"][0]
    results = []
    for identifier in identifiers:
        entry = copy.deepcopy(template)
        entry["metadata"]["identifier"] = [identifier]
        results.append(entry)
    return json.dumps({"totalResults": total, "results": results}).encode()


class _PagedTransport:
    def __init__(self, pages: list[bytes]) -> None:
        self.pages = pages
        self.requests: list[HttpRequest] = []

    def __call__(self, request: HttpRequest) -> bytes:
        self.requests.append(request)
        return self.pages[len(self.requests) - 1]


def test_all_pages_are_fetched_until_total_is_reached() -> None:
    transport = _PagedTransport([_page(150, ["A", "B"]), _page(150, ["C"])])
    opportunities = fetch_eu_portal_opportunities(transport, CONTEXT)
    assert [o.source_id for o in opportunities] == ["A", "B", "C"]
    assert len(transport.requests) == 2
    assert "pageNumber=2" in transport.requests[1].url


def test_request_is_a_multipart_post_with_query_and_languages() -> None:
    transport = _PagedTransport([_page(1, ["A"])])
    fetch_eu_portal_opportunities(transport, CONTEXT)
    request = transport.requests[0]
    assert request.method == "POST"
    assert dict(request.headers)["Content-Type"].startswith("multipart/form-data; boundary=")
    assert b'name="query"' in (request.body or b"")


def test_request_sorts_by_deadline_so_paging_is_stable() -> None:
    transport = _PagedTransport([_page(1, ["A"])])
    fetch_eu_portal_opportunities(transport, CONTEXT)
    body = (transport.requests[0].body or b"").decode("utf-8")
    assert 'name="sort"' in body
    assert '"field": "deadlineDate"' in body and '"order": "ASC"' in body


def test_duplicate_topics_across_pages_are_listed_once() -> None:
    transport = _PagedTransport([_page(150, ["A", "B"]), _page(150, ["B", "C"])])
    opportunities = fetch_eu_portal_opportunities(transport, CONTEXT)
    assert [o.source_id for o in opportunities] == ["A", "B", "C"]


def test_runtime_error_answer_becomes_a_source_fetch_error() -> None:
    body = b'{"apiVersion":"2.155","type":"runtimeError","message":"An internal error occurred"}'
    with pytest.raises(SourceFetchError, match="EU Funding"):
        fetch_eu_portal_opportunities(RecordingTransport(body), CONTEXT)
