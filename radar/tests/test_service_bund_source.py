from datetime import date

import pytest

from radar.http_transport import SourceFetchError
from radar.opportunity_model import RunContext
from radar.sources.service_bund_source import (
    SEARCH_TERMS,
    fetch_service_bund_opportunities,
    parse_service_bund_results,
)
from tests.conftest import RecordingTransport, load_fixture

TODAY = date(2026, 10, 11)
CONTEXT = RunContext(correlation_id="test-run", today=TODAY)
PAGE = load_fixture("service_bund_search.html").decode("utf-8")


def test_every_result_with_a_future_deadline_is_parsed() -> None:
    assert len(parse_service_bund_results(PAGE, TODAY)) == 4


def test_fields_are_mapped_and_soft_hyphens_removed() -> None:
    first = parse_service_bund_results(PAGE, TODAY)[0]
    assert first.title == "Buchungsplattform Bike-Verleihnetzwerk BLOCKLINE"
    assert first.buyer == "Tourismusverband Erzgebirge e.V."
    assert first.deadline == date(2026, 10, 26)
    assert first.source == "service_bund"
    assert first.source_id == "7066863"


def test_titles_the_site_escaped_twice_are_readable() -> None:
    doubly_escaped = PAGE.replace("BLOCK\u00adLI\u00adNE", "&amp;quot;BLOCKLINE&amp;quot;")
    assert parse_service_bund_results(doubly_escaped, TODAY)[0].title.endswith('"BLOCKLINE"')


def test_the_link_is_absolute_and_has_no_session_id() -> None:
    first = parse_service_bund_results(PAGE, TODAY)[0]
    assert first.url == "https://www.service.bund.de/IMPORTE/Ausschreibungen/evergabede/2026/10/7066863.html"


def test_results_past_their_deadline_are_dropped() -> None:
    assert parse_service_bund_results(PAGE, date(2026, 10, 27)) != parse_service_bund_results(PAGE, TODAY)
    assert len(parse_service_bund_results(PAGE, date(2026, 11, 1))) == 0


def test_fetch_searches_every_term_and_removes_duplicates() -> None:
    transport = RecordingTransport(PAGE.encode("utf-8"))
    opportunities = fetch_service_bund_opportunities(transport, CONTEXT)
    assert len(transport.requests) == len(SEARCH_TERMS)
    assert len(opportunities) == 4


def test_a_page_in_an_unknown_format_is_reported_as_a_source_failure() -> None:
    with pytest.raises(SourceFetchError, match="unexpected format"):
        fetch_service_bund_opportunities(RecordingTransport(b"<html>maintenance</html>"), CONTEXT)
