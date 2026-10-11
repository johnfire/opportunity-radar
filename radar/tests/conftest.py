import json
from pathlib import Path

import pytest

from radar.http_transport import HttpRequest, Transport

FIXTURE_DIRECTORY = Path(__file__).resolve().parent.parent / "fixtures"


def load_fixture(name: str) -> bytes:
    return (FIXTURE_DIRECTORY / name).read_bytes()


def load_fixture_json(name: str) -> dict[str, object]:
    loaded: dict[str, object] = json.loads(load_fixture(name))
    return loaded


@pytest.fixture
def transport_returning() -> "type[RecordingTransport]":
    return RecordingTransport


class RecordingTransport:
    """A fake network: answers every request with the same bytes and remembers what was asked."""

    def __init__(self, answer: bytes) -> None:
        self.answer = answer
        self.requests: list[HttpRequest] = []

    def __call__(self, request: HttpRequest) -> bytes:
        self.requests.append(request)
        return self.answer


def as_transport(recording: RecordingTransport) -> Transport:
    return recording


@pytest.fixture(autouse=True)
def no_jev_key_file(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Tests never read the real key file or call Jev unless a test says so."""
    monkeypatch.setenv("RADAR_JEV_ENV_FILE", str(tmp_path / "no-such-jev.env"))
