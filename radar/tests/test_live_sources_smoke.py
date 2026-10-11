"""Opt-in checks against the real internet: RADAR_NETWORK_TESTS=1 pytest -m network"""

import os
from datetime import date

import pytest

from radar.http_transport import fetch_over_network
from radar.opportunity_model import RunContext
from radar.source_registry import SOURCES

pytestmark = [
    pytest.mark.network,
    pytest.mark.skipif(os.environ.get("RADAR_NETWORK_TESTS") != "1", reason="set RADAR_NETWORK_TESTS=1"),
]


@pytest.mark.parametrize("source_name", ["koinno", "eu_portal", "ted", "bmftr", "service_bund", "sprind"])
def test_live_source_returns_opportunities_with_the_expected_fields(source_name: str) -> None:
    context = RunContext("smoke", date.today())
    opportunities = SOURCES[source_name].fetch(fetch_over_network, context)
    assert opportunities, f"{source_name} returned nothing; its feed may have changed"
    first = opportunities[0]
    assert first.title and first.url.startswith("http")
