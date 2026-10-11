from datetime import date

import pytest

from radar.http_transport import SourceFetchError
from radar.opportunity_model import RunContext
from radar.sources.koinno_source import fetch_koinno_opportunities, parse_koinno_challenges
from tests.conftest import RecordingTransport, load_fixture, load_fixture_json

CONTEXT = RunContext(correlation_id="test-run", today=date(2026, 10, 11))


def test_only_challenges_open_for_submissions_are_kept() -> None:
    opportunities = parse_koinno_challenges(load_fixture_json("koinno_challenges.json"))
    assert [o.source_id for o in opportunities] == [
        "6abd55f6f321e1a16ef744a0",
        "6ab50896f321e1a16ef58136",
        "6ab24230f321e1a16ef4f8e3",
    ]


def test_last_day_is_start_plus_weeks_minus_one_day_in_berlin_time() -> None:
    opportunities = {
        o.source_id: o for o in parse_koinno_challenges(load_fixture_json("koinno_challenges.json"))
    }
    assert opportunities["6abd55f6f321e1a16ef744a0"].deadline == date(2026, 10, 28)
    assert opportunities["6ab50896f321e1a16ef58136"].deadline == date(2026, 10, 25)
    assert opportunities["6ab24230f321e1a16ef4f8e3"].deadline == date(2026, 11, 3)


def test_fields_are_mapped_from_the_challenge() -> None:
    first = parse_koinno_challenges(load_fixture_json("koinno_challenges.json"))[0]
    assert first.source == "koinno"
    assert first.title == "Stellung von Mobilen Sanitäranlagen"
    assert first.buyer == "Bundeswehr-Dienstleistungszentrum Rostock"
    assert first.url == "https://app.koinnovationsplatz.de/challenges/6abd55f6f321e1a16ef744a0"
    assert first.amount_text == "keine Vergütung (Markterkundung)"
    assert "<" not in first.summary and len(first.summary) <= 300


def test_fetch_requests_the_public_api_and_parses_the_answer() -> None:
    transport = RecordingTransport(load_fixture("koinno_challenges.json"))
    opportunities = fetch_koinno_opportunities(transport, CONTEXT)
    assert len(opportunities) == 3
    assert transport.requests[0].url.startswith("https://app.koinnovationsplatz.de/api/challenges?")
    assert "pageSize=200" in transport.requests[0].url


def test_invalid_json_becomes_a_source_fetch_error() -> None:
    with pytest.raises(SourceFetchError, match="KOINNOvationsplatz"):
        fetch_koinno_opportunities(RecordingTransport(b"<html>not json</html>"), CONTEXT)


def test_unexpected_shape_becomes_a_source_fetch_error() -> None:
    with pytest.raises(SourceFetchError, match="KOINNOvationsplatz"):
        fetch_koinno_opportunities(RecordingTransport(b'{"unexpected": 1}'), CONTEXT)
