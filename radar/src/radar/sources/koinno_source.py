"""KOINNOvationsplatz: public buyers' market soundings. Uses the platform's public JSON feed."""

import json
from datetime import date, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from radar.http_transport import HttpRequest, SourceFetchError, Transport
from radar.opportunity_model import Opportunity, RunContext
from radar.plain_text_extraction import extract_plain_text, shorten_text

SOURCE_NAME = "koinno"
BASE_URL = "https://app.koinnovationsplatz.de"
FEED_URL = f"{BASE_URL}/api/challenges?page=1&pageSize=200&sort=-phases.start"
OPEN_PHASE = "CallForSolutions"
NO_PAYMENT_TEXT = "keine Vergütung (Markterkundung)"
BERLIN = ZoneInfo("Europe/Berlin")
SUMMARY_LENGTH = 300


def _last_day_for_submissions(phases: dict[str, Any]) -> date | None:
    start_text = phases.get("start")
    weeks = phases.get("callForSolutionsDuration")
    if not isinstance(start_text, str) or not isinstance(weeks, int):
        return None
    start = datetime.fromisoformat(start_text.replace("Z", "+00:00")).astimezone(BERLIN)
    return (start + timedelta(weeks=weeks) - timedelta(days=1)).date()


def _opportunity_from_challenge(challenge: dict[str, Any]) -> Opportunity:
    description = challenge["description"]
    return Opportunity(
        source=SOURCE_NAME,
        source_id=challenge["_id"],
        title=description["title"].strip(),
        buyer=challenge["owner"]["name"].strip(),
        url=f"{BASE_URL}/challenges/{challenge['_id']}",
        deadline=_last_day_for_submissions(challenge.get("phases", {})),
        amount_text=NO_PAYMENT_TEXT,
        summary=shorten_text(extract_plain_text(description.get("description")), SUMMARY_LENGTH),
    )


def parse_koinno_challenges(payload: dict[str, Any]) -> list[Opportunity]:
    challenges = payload["docs"]
    return [_opportunity_from_challenge(c) for c in challenges if c.get("currentPhase") == OPEN_PHASE]


def fetch_koinno_opportunities(transport: Transport, context: RunContext) -> list[Opportunity]:
    raw = transport(HttpRequest(url=FEED_URL))
    try:
        return parse_koinno_challenges(json.loads(raw))
    except (ValueError, KeyError, TypeError, AttributeError) as error:
        raise SourceFetchError(f"KOINNOvationsplatz answered in an unexpected format ({error!r})") from error
