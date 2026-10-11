from datetime import date

import pytest

from radar.http_transport import SourceFetchError
from radar.opportunity_model import RunContext
from radar.sources.sprind_source import fetch_sprind_opportunities, parse_sprind_challenges
from tests.conftest import RecordingTransport, load_fixture

TODAY = date(2026, 10, 11)
CONTEXT = RunContext(correlation_id="test-run", today=TODAY)
PAGE = load_fixture("sprind_challenges.html").decode("utf-8")


def test_only_cards_badged_apply_now_are_open_calls() -> None:
    assert [o.source_id for o in parse_sprind_challenges(PAGE, TODAY)] == [
        "engineering-microbial-consortia",
        "next-frontier-robotics",
    ]


def test_fields_are_mapped_from_the_card() -> None:
    first = parse_sprind_challenges(PAGE, TODAY)[0]
    assert first.source == "sprind"
    assert first.title == "Engineering Microbial Consortia"
    assert first.buyer == "SPRIND"
    assert first.url == "https://www.sprind.org/en/actions/challenges/engineering-microbial-consortia"
    assert first.deadline == date(2026, 11, 16)
    assert "circular biomanufacturing" in first.summary


def test_a_deadline_without_a_year_means_the_next_such_day() -> None:
    robotics = parse_sprind_challenges(PAGE, TODAY)[1]
    assert robotics.deadline == date(2026, 10, 22)
    next_year = parse_sprind_challenges(PAGE, date(2026, 10, 23))[1]
    assert next_year.deadline == date(2027, 10, 22)


def test_a_card_without_a_readable_deadline_is_still_reported() -> None:
    undated = PAGE.replace("Apply by November 16, 2026.", "Apply soon.")
    assert parse_sprind_challenges(undated, TODAY)[0].deadline is None


def test_fetch_reads_the_challenges_page() -> None:
    transport = RecordingTransport(PAGE.encode("utf-8"))
    assert len(fetch_sprind_opportunities(transport, CONTEXT)) == 2
    assert transport.requests[0].url == "https://www.sprind.org/en/challenges/"


def test_a_page_without_cards_is_reported_as_a_source_failure() -> None:
    with pytest.raises(SourceFetchError, match="layout"):
        fetch_sprind_opportunities(RecordingTransport(b"<html>maintenance</html>"), CONTEXT)
