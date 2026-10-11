import json
from pathlib import Path

from radar.audit_log import AuditEntry, append_audit_entry


def an_entry(action: str = "fetch_source") -> AuditEntry:
    return AuditEntry(
        timestamp="2026-10-11T08:00:00+02:00",
        correlation_id="run-1",
        actor="radar-bot",
        action=action,
        target="koinno",
        outcome="ok",
        detail="3 opportunities",
    )


def test_entry_is_appended_as_one_json_line(tmp_path: Path) -> None:
    path = tmp_path / "audit" / "audit.jsonl"
    append_audit_entry(path, an_entry())
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["actor"] == "radar-bot"
    assert json.loads(lines[0])["correlation_id"] == "run-1"


def test_existing_entries_are_never_rewritten(tmp_path: Path) -> None:
    path = tmp_path / "audit.jsonl"
    append_audit_entry(path, an_entry("first"))
    first_line = path.read_text(encoding="utf-8").splitlines()[0]
    append_audit_entry(path, an_entry("second"))
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == first_line and len(lines) == 2


def test_a_failure_to_write_does_not_raise(tmp_path: Path) -> None:
    blocked = tmp_path / "file-not-dir"
    blocked.write_text("x", encoding="utf-8")
    append_audit_entry(blocked / "audit.jsonl", an_entry())  # parent is a file; must not crash the run
