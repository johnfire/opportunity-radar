import json
from datetime import date
from pathlib import Path

import pytest

from radar.audit_log import ACTOR_NAME
from radar.http_transport import SourceFetchError, Transport
from radar.opportunity_model import Opportunity, RunContext
from radar.radar_run_orchestrator import DigestWriteError, RadarPaths, RunReport, run_radar
from radar.source_registry import SourceDefinition

TODAY = date(2026, 10, 11)
CONTEXT = RunContext("run-7", TODAY)


def an_opportunity(
    source: str, source_id: str, title: str, deadline: date | None = date(2026, 12, 1)
) -> Opportunity:
    return Opportunity(source, source_id, title, "Buyer", f"https://x/{source_id}", deadline, None, "")


def a_source(name: str, items: list[Opportunity]) -> SourceDefinition:
    def fetch(_: Transport, __: RunContext) -> list[Opportunity]:
        return items

    return SourceDefinition(name, fetch)


def a_failing_source(name: str, error: Exception) -> SourceDefinition:
    def fetch(_: Transport, __: RunContext) -> list[Opportunity]:
        raise error

    return SourceDefinition(name, fetch)


class NotifierSpy:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []

    def __call__(self, title: str, message: str) -> bool:
        self.messages.append((title, message))
        return True


def never_called_transport(_: object) -> bytes:
    raise AssertionError("fake sources must not use the network")


@pytest.fixture
def paths(tmp_path: Path) -> RadarPaths:
    (tmp_path / "config").mkdir()
    (tmp_path / "config" / "keywords.txt").write_text("software | 2\ndaten\n", encoding="utf-8")
    (tmp_path / "config" / "exclusions.txt").write_text("lizenz\n", encoding="utf-8")
    (tmp_path / "config" / "manual_checks.txt").write_text(
        "ZIM | https://zim.de | blocked\n", encoding="utf-8"
    )
    return RadarPaths(tmp_path)


def run(
    paths: RadarPaths,
    sources: list[SourceDefinition],
    notifier: NotifierSpy,
    context: RunContext = CONTEXT,
) -> RunReport:
    return run_radar("weekly", never_called_transport, context, paths, notifier, sources)


def test_digest_lists_new_matching_items_and_hides_excluded_ones(paths: RadarPaths) -> None:
    items = [
        an_opportunity("ted", "1", "Software für Verwaltung"),
        an_opportunity("ted", "2", "Software Lizenzen"),
        an_opportunity("ted", "3", "Straßenreinigung"),
    ]
    report = run(paths, [a_source("ted", items)], NotifierSpy())
    text = report.digest_path.read_text(encoding="utf-8")
    assert "Software für Verwaltung" in text
    assert "Software Lizenzen" not in text
    assert "Straßenreinigung" not in text
    assert "1 new items were hidden by your exclusion rules" in text
    assert "1 new items matched no keyword" in text


def test_a_source_marked_show_everything_lists_new_items_even_without_keyword_matches(
    paths: RadarPaths,
) -> None:
    items = [an_opportunity("koinno", "1", "Straßenreinigung Hamburg")]
    curated = SourceDefinition("koinno", lambda _t, _c: items, shows_everything_new=True)
    report = run(paths, [curated], NotifierSpy())
    assert "Straßenreinigung Hamburg" in report.digest_path.read_text(encoding="utf-8")


def test_show_everything_does_not_override_exclusion_rules(paths: RadarPaths) -> None:
    items = [an_opportunity("koinno", "1", "Software Lizenzen")]
    curated = SourceDefinition("koinno", lambda _t, _c: items, shows_everything_new=True)
    report = run(paths, [curated], NotifierSpy())
    assert "Software Lizenzen" not in report.digest_path.read_text(encoding="utf-8")


def test_a_failing_source_does_not_stop_the_others(paths: RadarPaths) -> None:
    sources = [
        a_failing_source("eu_portal", SourceFetchError("HTTP 500")),
        a_source("ted", [an_opportunity("ted", "1", "Software A")]),
    ]
    report = run(paths, sources, NotifierSpy())
    text = report.digest_path.read_text(encoding="utf-8")
    assert "| eu_portal | FAILED | 0 | 0 | HTTP 500 |" in text
    assert "Software A" in text
    assert report.failed_sources == ["eu_portal"]


def test_an_unexpected_bug_in_one_source_is_contained_too(paths: RadarPaths) -> None:
    sources = [
        a_failing_source("koinno", KeyError("boom")),
        a_source("ted", [an_opportunity("ted", "1", "Daten X")]),
    ]
    report = run(paths, sources, NotifierSpy())
    assert report.failed_sources == ["koinno"]
    assert "Daten X" in report.digest_path.read_text(encoding="utf-8")


def test_second_run_reports_nothing_new_but_flags_items_closing_soon(paths: RadarPaths) -> None:
    items = [an_opportunity("ted", "1", "Software dringend", deadline=date(2026, 10, 20))]
    run(paths, [a_source("ted", items)], NotifierSpy())
    second = run(paths, [a_source("ted", items)], NotifierSpy())
    text = second.digest_path.read_text(encoding="utf-8")
    assert "Nothing new matched your keywords." in text
    assert "## Closing within 14 days" in text and "Software dringend" in text
    assert second.digest_path.name.endswith("-2.md")


def test_state_is_not_updated_for_a_failed_source(paths: RadarPaths) -> None:
    run(paths, [a_failing_source("ted", SourceFetchError("down"))], NotifierSpy())
    assert not paths.state_file.exists() or json.loads(paths.state_file.read_text(encoding="utf-8")) == {}


def test_notification_summarises_the_run(paths: RadarPaths) -> None:
    notifier = NotifierSpy()
    run(
        paths,
        [a_source("ted", [an_opportunity("ted", "1", "Software A"), an_opportunity("ted", "2", "Daten B")])],
        notifier,
    )
    assert len(notifier.messages) == 1
    assert "2 new" in notifier.messages[0][1]


def test_failed_sources_are_mentioned_in_the_notification(paths: RadarPaths) -> None:
    notifier = NotifierSpy()
    run(paths, [a_failing_source("ted", SourceFetchError("down"))], notifier)
    assert "failed: ted" in notifier.messages[0][1]


def test_every_source_run_is_written_to_the_audit_log(paths: RadarPaths) -> None:
    run(paths, [a_source("ted", [an_opportunity("ted", "1", "Software A")])], NotifierSpy())
    entries = [json.loads(line) for line in paths.audit_file.read_text(encoding="utf-8").splitlines()]
    actions = [(e["action"], e["target"], e["outcome"]) for e in entries]
    assert ("fetch_source", "ted", "ok") in actions
    assert any(e["action"] == "write_digest" for e in entries)
    assert {e["actor"] for e in entries} == {ACTOR_NAME}
    assert {e["correlation_id"] for e in entries} == {"run-7"}


def test_missing_keyword_file_shows_everything_and_warns(paths: RadarPaths) -> None:
    paths.keywords_file.unlink()
    report = run(paths, [a_source("ted", [an_opportunity("ted", "1", "Straßenreinigung")])], NotifierSpy())
    text = report.digest_path.read_text(encoding="utf-8")
    assert "Straßenreinigung" in text
    assert "keyword file" in text


def test_manual_checks_appear_in_the_digest(paths: RadarPaths) -> None:
    report = run(paths, [a_source("ted", [])], NotifierSpy())
    assert "- ZIM: https://zim.de (blocked)" in report.digest_path.read_text(encoding="utf-8")


def test_corrupt_state_file_is_reported_as_a_warning(paths: RadarPaths) -> None:
    paths.state_file.parent.mkdir(parents=True)
    paths.state_file.write_text("{ broken", encoding="utf-8")
    report = run(paths, [a_source("ted", [an_opportunity("ted", "1", "Software A")])], NotifierSpy())
    assert "corrupt" in report.digest_path.read_text(encoding="utf-8")


def test_unwritable_digest_directory_raises_and_leaves_state_untouched(paths: RadarPaths) -> None:
    paths.digest_directory.parent.mkdir(parents=True, exist_ok=True)
    paths.digest_directory.write_text("a file where a folder should be", encoding="utf-8")
    with pytest.raises(DigestWriteError):
        run(paths, [a_source("ted", [an_opportunity("ted", "1", "Software A")])], NotifierSpy())
    assert not paths.state_file.exists()
