import json
import shutil
from pathlib import Path

import pytest

from radar.command_line import main
from radar.http_transport import HttpRequest
from tests.conftest import FIXTURE_DIRECTORY, load_fixture

CONFIG_DIRECTORY = Path(__file__).resolve().parent.parent / "config"


class RoutingTransport:
    """Answers each source's URL with its captured real response, so the whole run works offline."""

    def __init__(self) -> None:
        self.requested: list[str] = []

    def __call__(self, request: HttpRequest) -> bytes:
        self.requested.append(request.url)
        if "koinnovationsplatz" in request.url:
            return load_fixture("koinno_challenges.json")
        if "api.tech.ec.europa.eu" in request.url:
            return load_fixture("eu_portal_search.json")
        if "api.ted.europa.eu" in request.url:
            return load_fixture("ted_search.json")
        raise AssertionError(f"unexpected request to {request.url}")


class NotifierSpy:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str]] = []

    def __call__(self, title: str, message: str) -> bool:
        self.messages.append((title, message))
        return True


@pytest.fixture
def root(tmp_path: Path) -> Path:
    shutil.copytree(CONFIG_DIRECTORY, tmp_path / "config")
    return tmp_path


def test_weekly_run_writes_a_digest_with_items_from_every_source(root: Path) -> None:
    notifier = NotifierSpy()
    exit_code = main(["run", "--group", "weekly", "--root", str(root)], RoutingTransport(), notifier)
    assert exit_code == 0
    digests = list((root / "digests").glob("*-weekly.md"))
    assert len(digests) == 1
    text = digests[0].read_text(encoding="utf-8")
    assert "| koinno | ok |" in text and "| eu_portal | ok |" in text and "| ted | ok |" in text
    assert "GeoOpenSource" in text
    assert len(notifier.messages) == 1


def test_run_leaves_state_and_audit_log_behind(root: Path) -> None:
    main(["run", "--group", "weekly", "--root", str(root)], RoutingTransport(), NotifierSpy())
    state = json.loads((root / "state" / "seen.json").read_text(encoding="utf-8"))
    assert "ted:670742-2026" in state
    audit_lines = (root / "audit" / "audit.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(audit_lines) >= 4


def test_a_second_weekly_run_finds_nothing_new(root: Path) -> None:
    main(["run", "--group", "weekly", "--root", str(root)], RoutingTransport(), NotifierSpy())
    main(["run", "--group", "weekly", "--root", str(root)], RoutingTransport(), NotifierSpy())
    second = sorted((root / "digests").glob("*-weekly-2.md"))[0].read_text(encoding="utf-8")
    assert "Nothing new matched your keywords." in second


def test_unknown_group_exits_with_code_3(root: Path) -> None:
    assert main(["run", "--group", "daily", "--root", str(root)], RoutingTransport(), NotifierSpy()) == 3


def test_unwritable_digest_directory_exits_with_code_2(root: Path) -> None:
    (root / "digests").write_text("a file, not a folder", encoding="utf-8")
    assert main(["run", "--group", "weekly", "--root", str(root)], RoutingTransport(), NotifierSpy()) == 2


def test_fixtures_exist_for_every_routed_source() -> None:
    for name in ("koinno_challenges.json", "eu_portal_search.json", "ted_search.json"):
        assert (FIXTURE_DIRECTORY / name).exists()
