import json
from datetime import date
from pathlib import Path

import pytest

from radar.http_transport import HttpRequest, SourceFetchError
from radar.jev_fit_scoring import (
    MAX_CONSECUTIVE_FAILURES,
    build_request,
    judge_many,
    parse_judgment,
    read_api_key,
)
from radar.opportunity_model import Opportunity

ANSWER = json.dumps(
    {
        "model": "jev-1.13.0",
        "answers": {
            "could_solve": {"type": "noul", "noul": 0.81},
            "call_kind": {
                "type": "choice",
                "choice": "service_tender",
                "probabilities": {},
                "confidence": 0.9,
            },
        },
    }
).encode()


def an_opportunity(title: str = "Software für Fahrradmanagement") -> Opportunity:
    return Opportunity("ted", title, title, "Fraunhofer", "https://x", date(2026, 11, 1), None, "S" * 2000)


def test_the_api_key_is_read_from_an_env_file(tmp_path: Path) -> None:
    env_file = tmp_path / "jev.env"
    env_file.write_text("# comment\nTYPESAFE_API_KEY='abc123'\n", encoding="utf-8")
    assert read_api_key(env_file) == "abc123"


def test_a_missing_file_or_key_gives_none(tmp_path: Path) -> None:
    assert read_api_key(tmp_path / "missing.env") is None
    (tmp_path / "other.env").write_text("OTHER=1\n", encoding="utf-8")
    assert read_api_key(tmp_path / "other.env") is None


def test_the_request_sends_only_public_text_with_a_shortened_summary() -> None:
    request = build_request(an_opportunity(), "secret-key")
    body = json.loads(request.body or b"")
    assert set(body["state"]["opportunity"]) == {"title", "buyer", "summary"}
    assert len(body["state"]["opportunity"]["summary"]) <= 600
    assert ("Authorization", "Bearer secret-key") in request.headers
    assert "secret-key" not in (request.body or b"").decode()


def test_an_answer_is_parsed_into_a_judgment() -> None:
    judgment = parse_judgment(ANSWER)
    assert judgment.could_solve == pytest.approx(0.81) and judgment.call_kind == "service_tender"


def test_an_unexpected_answer_is_a_fetch_error() -> None:
    with pytest.raises(SourceFetchError, match="unexpected format"):
        parse_judgment(b'{"answers": {}}')


def test_every_item_gets_a_judgment_keyed_by_its_key() -> None:
    items = [an_opportunity("a"), an_opportunity("b")]
    judgments, warnings = judge_many(items, lambda request: ANSWER, "k")
    assert set(judgments) == {"ted:a", "ted:b"} and warnings == []


def test_one_failing_item_does_not_stop_the_others() -> None:
    def flaky(request: HttpRequest) -> bytes:
        if b'"title": "bad"' in (request.body or b""):
            raise SourceFetchError("HTTP 500")
        return ANSWER

    judgments, warnings = judge_many([an_opportunity("bad"), an_opportunity("good")], flaky, "k")
    assert list(judgments) == ["ted:good"]
    assert "1 of 2" in warnings[0] or "judged 1 of 2" in warnings[0]


def test_a_service_that_is_down_stops_after_a_few_failures() -> None:
    calls: list[int] = []

    def down(request: HttpRequest) -> bytes:
        calls.append(1)
        raise SourceFetchError("HTTP 503")

    judgments, warnings = judge_many([an_opportunity(str(n)) for n in range(50)], down, "k")
    assert judgments == {} and len(calls) == MAX_CONSECUTIVE_FAILURES and warnings
