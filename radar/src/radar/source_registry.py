"""Which sources exist and which schedule group runs them."""

from collections.abc import Callable
from dataclasses import dataclass

from radar.http_transport import Transport
from radar.opportunity_model import Opportunity, RunContext
from radar.sources.bmftr_source import fetch_bmftr_opportunities
from radar.sources.eu_portal_source import fetch_eu_portal_opportunities
from radar.sources.koinno_source import fetch_koinno_opportunities
from radar.sources.service_bund_source import fetch_service_bund_opportunities
from radar.sources.ted_source import fetch_ted_opportunities

SourceFetcher = Callable[[Transport, RunContext], list[Opportunity]]


@dataclass(frozen=True)
class SourceDefinition:
    name: str
    fetch: SourceFetcher
    shows_everything_new: bool = False  # small curated lists: show every new item, not only keyword matches


SOURCES: dict[str, SourceDefinition] = {
    "koinno": SourceDefinition("koinno", fetch_koinno_opportunities, shows_everything_new=True),
    "eu_portal": SourceDefinition("eu_portal", fetch_eu_portal_opportunities),
    "ted": SourceDefinition("ted", fetch_ted_opportunities),
    "bmftr": SourceDefinition("bmftr", fetch_bmftr_opportunities),
    "service_bund": SourceDefinition("service_bund", fetch_service_bund_opportunities),
}

# weekly (Saturday): API sources that are cheap and rarely break.
# twice-monthly (1st and 15th): page-based sources, added one by one.
GROUPS: dict[str, tuple[str, ...]] = {
    "weekly": ("koinno", "eu_portal", "ted"),
    "twice-monthly": ("bmftr", "service_bund"),
}


def sources_for_group(group: str) -> list[SourceDefinition]:
    if group not in GROUPS:
        raise ValueError(f"unknown group {group!r}; choose one of {sorted(GROUPS)}")
    return [SOURCES[name] for name in GROUPS[group]]
