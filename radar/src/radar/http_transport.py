"""The single place where the radar touches the network. Everything else gets a Transport injected."""

import time
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass

USER_AGENT = "opportunity-radar/0.1 (personal research tool; polite, low-frequency)"


class SourceFetchError(Exception):
    """A source could not be read. The message is shown in the digest's source-health section."""


@dataclass(frozen=True)
class HttpRequest:
    url: str
    method: str = "GET"
    headers: tuple[tuple[str, str], ...] = ()
    body: bytes | None = None


Transport = Callable[[HttpRequest], bytes]


def _build_urllib_request(request: HttpRequest) -> urllib.request.Request:
    prepared = urllib.request.Request(  # noqa: S310 - schemes are fixed by the source modules
        request.url, data=request.body, method=request.method
    )
    prepared.add_header("User-Agent", USER_AGENT)
    for name, value in request.headers:
        prepared.add_header(name, value)
    return prepared


def _is_worth_retrying(error: Exception) -> bool:
    if isinstance(error, urllib.error.HTTPError):
        return error.code >= 500
    return True


def fetch_over_network(
    request: HttpRequest,
    timeout_seconds: float = 40.0,
    attempts: int = 2,
    pause_seconds: float = 3.0,
) -> bytes:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            with urllib.request.urlopen(  # noqa: S310
                _build_urllib_request(request), timeout=timeout_seconds
            ) as response:
                return bytes(response.read())
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            last_error = error
            if not _is_worth_retrying(error) or attempt == attempts - 1:
                break
            time.sleep(pause_seconds)
    raise SourceFetchError(_describe(request, last_error))


def _describe(request: HttpRequest, error: Exception | None) -> str:
    if isinstance(error, urllib.error.HTTPError):
        return f"{request.url} answered HTTP {error.code}"
    return f"{request.url} could not be reached ({error})"
