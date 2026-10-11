from datetime import date

import pytest

from radar.http_transport import SourceFetchError
from radar.opportunity_model import RunContext
from radar.sources.bmftr_source import fetch_bmftr_opportunities, parse_bmftr_announcements
from tests.conftest import RecordingTransport, load_fixture

TODAY = date(2026, 10, 11)
CONTEXT = RunContext(correlation_id="test-run", today=TODAY)
PAGE = load_fixture("bmftr_announcements.html").decode("utf-8")


def test_only_announcements_with_a_future_deadline_are_kept() -> None:
    opportunities = parse_bmftr_announcements(PAGE, TODAY)
    assert len(opportunities) == 5
    assert all(o.deadline is not None and o.deadline >= TODAY for o in opportunities)


def test_fields_are_mapped_from_the_table_row() -> None:
    first = parse_bmftr_announcements(PAGE, TODAY)[0]
    assert first.source == "bmftr"
    assert first.buyer == "BMFTR"
    assert first.deadline == date(2032, 12, 31)
    assert first.url.startswith("https://www.bmftr.bund.de/SharedDocs/Bekanntmachungen/")
    assert first.source_id == "1283_bekanntmachung"


def test_a_row_without_a_parsable_deadline_is_skipped() -> None:
    broken = PAGE.replace("31.12.2032", "laufend")
    assert len(parse_bmftr_announcements(broken, TODAY)) == 4


def test_fetch_requests_the_deadline_sorted_list() -> None:
    transport = RecordingTransport(PAGE.encode("utf-8"))
    opportunities = fetch_bmftr_opportunities(transport, CONTEXT)
    assert len(opportunities) == 5
    assert "sortOrder=dateOfExpiration_dt+desc" in transport.requests[0].url


def test_a_page_without_a_table_is_reported_as_a_source_failure() -> None:
    with pytest.raises(SourceFetchError, match="table"):
        fetch_bmftr_opportunities(RecordingTransport(b"<html>maintenance</html>"), CONTEXT)
