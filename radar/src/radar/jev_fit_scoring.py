"""Ask TypeSafe's Jev whether a small software and AI team could solve what an opportunity describes.

Advisory only: the answer is shown next to the keyword score and never hides an item. Only public text
(title, buyer, short summary) is sent. A failure here must never stop the digest, so every error is
caught per item and reported as a warning.
"""

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from radar.http_transport import HttpRequest, SourceFetchError, Transport
from radar.opportunity_model import Opportunity
from radar.plain_text_extraction import shorten_text

API_URL = "https://api.typesafe.ai/v1/systemone"
MODEL = "jev-latest"
KEY_NAME = "TYPESAFE_API_KEY"
SUMMARY_MAX_LENGTH = 600
MAX_CONSECUTIVE_FAILURES = 5
CALL_KINDS = {
    "funding_or_research_call": "A grant, prize or research programme that funds development work",
    "service_tender": "A public tender to buy software, data, consulting or engineering services",
    "goods_or_licence_purchase": "Buying goods, hardware, licences, subscriptions or routine supplies",
    "other": "Anything else",
}
_COULD_SOLVE = {
    "type": "noul",
    "instructions": {
        "question": (
            "Could a very small team (one freelance engineer skilled in software, AI, chip verification "
            "and process automation, plus a few hired specialists) deliver something that addresses the "
            "need or problem described in `opportunity`?"
        )
    },
    "criteria": {
        "true": "A software, AI, data, automation, electronics or engineering result a small team can build",
        "false": "Needs physical goods, construction, a large workforce, a product the buyer already named, "
        "or skills unrelated to software, AI and engineering",
    },
}
_CALL_KIND = {
    "type": "choice",
    "instructions": {"question": "What kind of offer is `opportunity`?"},
    "criteria": CALL_KINDS,
}


@dataclass(frozen=True)
class FitJudgment:
    could_solve: float
    call_kind: str


def read_api_key(env_file: Path) -> str | None:
    """Read TYPESAFE_API_KEY=... from a local env file. Returns None when the file or key is missing."""
    try:
        lines = env_file.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    for line in lines:
        name, _, value = line.strip().partition("=")
        if name.removeprefix("export ").strip() == KEY_NAME and value.strip():
            return value.strip().strip("\"'")
    return None


def build_request(opportunity: Opportunity, api_key: str) -> HttpRequest:
    state = {
        "title": opportunity.title,
        "buyer": opportunity.buyer,
        "summary": shorten_text(opportunity.summary, SUMMARY_MAX_LENGTH),
    }
    body = {
        "state": {"opportunity": state},
        "model": MODEL,
        "questions": {"could_solve": _COULD_SOLVE, "call_kind": _CALL_KIND},
    }
    return HttpRequest(
        url=API_URL,
        method="POST",
        headers=(("Content-Type", "application/json"), ("Authorization", f"Bearer {api_key}")),
        body=json.dumps(body).encode("utf-8"),
    )


def parse_judgment(raw: bytes) -> FitJudgment:
    try:
        answers: Mapping[str, Any] = json.loads(raw)["answers"]
        return FitJudgment(float(answers["could_solve"]["noul"]), str(answers["call_kind"]["choice"]))
    except (ValueError, KeyError, TypeError) as error:
        raise SourceFetchError(f"Jev answered in an unexpected format ({error!r})") from error


def judge_fit(opportunity: Opportunity, transport: Transport, api_key: str) -> FitJudgment:
    return parse_judgment(transport(build_request(opportunity, api_key)))


def judge_many(
    opportunities: list[Opportunity], transport: Transport, api_key: str
) -> tuple[dict[str, FitJudgment], list[str]]:
    """Judge each item on its own; stop early only when the service looks down. Never raises."""
    judgments: dict[str, FitJudgment] = {}
    failures_in_a_row, failed_total = 0, 0
    for opportunity in opportunities:
        try:
            judgments[opportunity.key] = judge_fit(opportunity, transport, api_key)
            failures_in_a_row = 0
        except SourceFetchError:
            failures_in_a_row, failed_total = failures_in_a_row + 1, failed_total + 1
            if failures_in_a_row >= MAX_CONSECUTIVE_FAILURES:
                break
    return judgments, _warnings(len(opportunities), len(judgments), failed_total)


def _warnings(requested: int, judged: int, failed: int) -> list[str]:
    if judged == requested:
        return []
    return [
        f"Jev judged {judged} of {requested} items ({failed} requests failed); "
        "the rest are shown without a Jev column value. / "
        f"Jev bewertete {judged} von {requested} Einträgen ({failed} Anfragen fehlgeschlagen)."
    ]
