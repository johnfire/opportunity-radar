"""Remembers which opportunities earlier digests already showed, so each digest lists only what is new."""

import json
import os
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from radar.opportunity_model import Opportunity


@dataclass(frozen=True)
class SeenRecord:
    first_seen: date
    last_seen: date


SeenState = dict[str, SeenRecord]


def load_seen_state(path: Path) -> tuple[SeenState, str | None]:
    """Returns the state and an optional warning. A corrupt file is set aside, never silently deleted."""
    if not path.exists():
        return {}, None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return {key: _record_from_json(value) for key, value in raw.items()}, None
    except (ValueError, KeyError, TypeError, AttributeError):
        set_aside = path.with_name(f"{path.name}.corrupt-{date.today().isoformat()}")
        path.rename(set_aside)
        return {}, f"seen-state file was corrupt; moved to {set_aside.name} and started fresh"


def _record_from_json(value: dict[str, str]) -> SeenRecord:
    return SeenRecord(date.fromisoformat(value["first_seen"]), date.fromisoformat(value["last_seen"]))


def save_seen_state(state: SeenState, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serializable = {
        key: {"first_seen": r.first_seen.isoformat(), "last_seen": r.last_seen.isoformat()}
        for key, r in sorted(state.items())
    }
    handle, temporary_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    with os.fdopen(handle, "w", encoding="utf-8") as temporary_file:
        json.dump(serializable, temporary_file, indent=1)
    os.replace(temporary_name, path)


def partition_new_and_known(
    opportunities: list[Opportunity], state: SeenState
) -> tuple[list[Opportunity], list[Opportunity]]:
    new = [o for o in opportunities if o.key not in state]
    known = [o for o in opportunities if o.key in state]
    return new, known


def update_seen_state(state: SeenState, opportunities: list[Opportunity], today: date) -> SeenState:
    updated = dict(state)
    for opportunity in opportunities:
        previous = updated.get(opportunity.key)
        first_seen = previous.first_seen if previous else today
        updated[opportunity.key] = SeenRecord(first_seen=first_seen, last_seen=today)
    return updated
