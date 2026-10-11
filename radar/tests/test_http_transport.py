import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from radar.http_transport import HttpRequest, SourceFetchError, fetch_over_network


class _ScriptedHandler(BaseHTTPRequestHandler):
    scripted_responses: list[tuple[int, bytes]] = []
    received: list[tuple[str, bytes]] = []

    def _reply(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""
        type(self).received.append((self.command, body))
        status, payload = type(self).scripted_responses.pop(0)
        self.send_response(status)
        self.end_headers()
        self.wfile.write(payload)

    do_GET = _reply  # noqa: N815 - the HTTP server dispatches on these exact names
    do_POST = _reply  # noqa: N815

    def log_message(self, format: str, *args: object) -> None:  # silence test output
        return


@pytest.fixture
def server() -> Iterator[tuple[HTTPServer, str]]:
    _ScriptedHandler.scripted_responses = []
    _ScriptedHandler.received = []
    httpd = HTTPServer(("127.0.0.1", 0), _ScriptedHandler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield httpd, f"http://127.0.0.1:{httpd.server_port}/"
    httpd.shutdown()


def test_get_returns_body_bytes(server: tuple[HTTPServer, str]) -> None:
    _ScriptedHandler.scripted_responses = [(200, b'{"ok": true}')]
    body = fetch_over_network(HttpRequest(url=server[1]), pause_seconds=0)
    assert body == b'{"ok": true}'


def test_post_sends_body_and_headers(server: tuple[HTTPServer, str]) -> None:
    _ScriptedHandler.scripted_responses = [(200, b"done")]
    request = HttpRequest(url=server[1], method="POST", body=b"payload", headers=(("X-Test", "1"),))
    fetch_over_network(request, pause_seconds=0)
    assert _ScriptedHandler.received == [("POST", b"payload")]


def test_server_error_is_retried_once(server: tuple[HTTPServer, str]) -> None:
    _ScriptedHandler.scripted_responses = [(503, b"busy"), (200, b"fine")]
    assert fetch_over_network(HttpRequest(url=server[1]), pause_seconds=0) == b"fine"


def test_repeated_server_error_raises_source_fetch_error(server: tuple[HTTPServer, str]) -> None:
    _ScriptedHandler.scripted_responses = [(500, b"x"), (500, b"x")]
    with pytest.raises(SourceFetchError, match="500"):
        fetch_over_network(HttpRequest(url=server[1]), pause_seconds=0)


def test_client_error_is_not_retried(server: tuple[HTTPServer, str]) -> None:
    _ScriptedHandler.scripted_responses = [(404, b"nope"), (200, b"never reached")]
    with pytest.raises(SourceFetchError, match="404"):
        fetch_over_network(HttpRequest(url=server[1]), pause_seconds=0)
    assert len(_ScriptedHandler.received) == 1


def test_unreachable_host_raises_source_fetch_error() -> None:
    with pytest.raises(SourceFetchError):
        fetch_over_network(HttpRequest(url="http://127.0.0.1:9/"), timeout_seconds=1, pause_seconds=0)
