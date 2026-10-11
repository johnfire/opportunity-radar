import json
from datetime import date
from typing import Any

import pytest

from radar.http_transport import HttpRequest, SourceFetchError
from radar.opportunity_model import RunContext
from radar.sources.ted_source import CPV_PREFIXES, fetch_ted_opportunities, parse_ted_notices
from tests.conftest import RecordingTransport, load_fixture, load_fixture_json

TODAY = date(2026, 10, 11)
CONTEXT = RunContext(correlation_id="test-run", today=TODAY)


def test_every_notice_with_a_future_deadline_is_kept() -> None:
    opportunities = parse_ted_notices(load_fixture_json("ted_search.json"), TODAY)
    assert len(opportunities) == 5
    assert all(o.deadline is not None and o.deadline >= TODAY for o in opportunities)


def test_fields_are_mapped_from_the_notice() -> None:
    first = parse_ted_notices(load_fixture_json("ted_search.json"), TODAY)[0]
    assert first.source == "ted"
    assert first.source_id == "670742-2026"
    assert first.buyer == "Dataport AöR"
    assert first.deadline == date(2026, 11, 3)
    assert first.url == "https://ted.europa.eu/en/notice/-/detail/670742-2026"


def test_title_drops_the_country_and_category_prefix() -> None:
    first = parse_ted_notices(load_fixture_json("ted_search.json"), TODAY)[0]
    assert first.title == "RV GeoOpenSource"


def test_notices_whose_deadlines_all_passed_are_dropped() -> None:
    payload: Any = load_fixture_json("ted_search.json")
    payload["notices"][0]["deadline-receipt-tender-date-lot"] = ["2026-09-01+02:00"]
    assert "670742-2026" not in [o.source_id for o in parse_ted_notices(payload, TODAY)]


def test_the_earliest_future_deadline_of_several_lots_is_used() -> None:
    payload: Any = load_fixture_json("ted_search.json")
    payload["notices"][0]["deadline-receipt-tender-date-lot"] = [
        "2026-12-01+01:00",
        "2026-10-20+02:00",
        "2026-09-01+02:00",
    ]
    first = parse_ted_notices(payload, TODAY)[0]
    assert first.deadline == date(2026, 10, 20)


def test_one_search_per_cpv_prefix_is_sent_with_a_deadline_filter() -> None:
    transport = RecordingTransport(load_fixture("ted_search.json"))
    fetch_ted_opportunities(transport, CONTEXT)
    queries = [json.loads(r.body or b"{}")["query"] for r in transport.requests]
    assert len(queries) == len(CPV_PREFIXES)
    assert all("deadline-receipt-tender-date-lot>=20261011" in q for q in queries)
    assert all("buyer-country=DEU" in q for q in queries)
    assert [f"classification-cpv={p}" in q for p, q in zip(CPV_PREFIXES, queries, strict=True)] == [
        True
    ] * len(queries)


def test_the_same_notice_found_by_two_searches_is_listed_once() -> None:
    transport = RecordingTransport(load_fixture("ted_search.json"))
    opportunities = fetch_ted_opportunities(transport, CONTEXT)
    assert len(opportunities) == 5


def test_post_request_asks_for_json() -> None:
    transport = RecordingTransport(load_fixture("ted_search.json"))
    fetch_ted_opportunities(transport, CONTEXT)
    request: HttpRequest = transport.requests[0]
    assert request.method == "POST"
    assert ("Content-Type", "application/json") in request.headers


def test_unexpected_answer_becomes_a_source_fetch_error() -> None:
    with pytest.raises(SourceFetchError, match="TED"):
        fetch_ted_opportunities(RecordingTransport(b'{"message": "bad query"}'), CONTEXT)


def test_estimated_value_is_shown_when_the_notice_gives_one() -> None:
    payload: Any = load_fixture_json("ted_search.json")
    payload["notices"][0]["estimated-value-lot"] = [1420168.07]
    payload["notices"][0]["estimated-value-cur-lot"] = ["EUR"]
    assert parse_ted_notices(payload, TODAY)[0].amount_text == "geschätzt 1.420.168 EUR"


def test_no_value_means_no_amount_text() -> None:
    assert parse_ted_notices(load_fixture_json("ted_search.json"), TODAY)[0].amount_text is None
