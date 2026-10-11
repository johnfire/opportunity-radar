"""Append-only record of everything the radar does: who acted, what, on what, and how it went."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

ACTOR_NAME = "radar-bot"


@dataclass(frozen=True)
class AuditEntry:
    timestamp: str
    correlation_id: str
    actor: str
    action: str
    target: str
    outcome: str
    detail: str


def append_audit_entry(path: Path, entry: AuditEntry) -> None:
    """Never raises: a broken audit file must not stop the radar from doing its job."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as audit_file:
            audit_file.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")
    except OSError:
        return
