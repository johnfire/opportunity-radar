import json
from datetime import date
from pathlib import Path

from radar.opportunity_model import Opportunity
from radar.seen_state_store import (
    SeenRecord,
    load_seen_state,
    partition_new_and_known,
    save_seen_state,
    update_seen_state,
)


def an_opportunity(source_id: str, deadline: date | None = date(2026, 11, 1)) -> Opportunity:
    return Opportunity("koinno", source_id, "T", "B", "https://x", deadline, None, "")


def test_missing_state_file_means_nothing_seen_yet(tmp_path: Path) -> None:
    state, warning = load_seen_state(tmp_path / "seen.json")
    assert state == {} and warning is None


def test_state_round_trips_through_the_file(tmp_path: Path) -> None:
    path = tmp_path / "state" / "seen.json"
    state = {"koinno:a": SeenRecord(first_seen=date(2026, 10, 1), last_seen=date(2026, 10, 8))}
    save_seen_state(state, path)
    loaded, warning = load_seen_state(path)
    assert loaded == state and warning is None


def test_corrupt_state_file_is_set_aside_and_reported(tmp_path: Path) -> None:
    path = tmp_path / "seen.json"
    path.write_text("{ not json", encoding="utf-8")
    state, warning = load_seen_state(path)
    assert state == {}
    assert warning is not None and "corrupt" in warning
    assert not path.exists()
    assert list(tmp_path.glob("seen.json.corrupt-*"))


def test_save_leaves_no_temporary_file_behind(tmp_path: Path) -> None:
    path = tmp_path / "seen.json"
    save_seen_state({}, path)
    assert sorted(p.name for p in tmp_path.iterdir()) == ["seen.json"]
    assert json.loads(path.read_text(encoding="utf-8")) == {}


def test_partition_separates_new_from_known() -> None:
    state = {"koinno:a": SeenRecord(date(2026, 10, 1), date(2026, 10, 1))}
    new, known = partition_new_and_known([an_opportunity("a"), an_opportunity("b")], state)
    assert [o.source_id for o in new] == ["b"]
    assert [o.source_id for o in known] == ["a"]


def test_update_keeps_first_seen_and_refreshes_last_seen() -> None:
    state = {"koinno:a": SeenRecord(date(2026, 10, 1), date(2026, 10, 1))}
    updated = update_seen_state(state, [an_opportunity("a"), an_opportunity("b")], date(2026, 10, 8))
    assert updated["koinno:a"] == SeenRecord(date(2026, 10, 1), date(2026, 10, 8))
    assert updated["koinno:b"] == SeenRecord(date(2026, 10, 8), date(2026, 10, 8))


def test_update_does_not_change_the_input_state() -> None:
    state = {"koinno:a": SeenRecord(date(2026, 10, 1), date(2026, 10, 1))}
    update_seen_state(state, [an_opportunity("b")], date(2026, 10, 8))
    assert list(state) == ["koinno:a"]
