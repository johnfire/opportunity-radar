"""Turns a run's findings into the markdown digest Chris reads."""

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from radar.keyword_scoring import ScoredOpportunity
from radar.opportunity_model import RunContext

CLOSING_SOON_DAYS = 14


@dataclass(frozen=True)
class SourceResult:
    source: str
    succeeded: bool
    found_count: int
    new_count: int
    error: str | None


@dataclass(frozen=True)
class ManualCheck:
    name: str
    url: str
    note: str


@dataclass(frozen=True)
class DigestInput:
    context: RunContext
    group: str
    new_items: list[ScoredOpportunity]
    closing_soon: list[ScoredOpportunity]
    hidden_by_rules: int
    unmatched_count: int
    source_results: list[SourceResult]
    manual_checks: list[ManualCheck]
    warnings: list[str]


def parse_manual_check_lines(text: str) -> list[ManualCheck]:
    checks: list[ManualCheck] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            name, url, note = (part.strip() for part in (stripped.split("|") + ["", ""])[:3])
            checks.append(ManualCheck(name, url, note))
    return checks


def next_digest_path(directory: Path, today: date, group: str) -> Path:
    base = f"{today.isoformat()}-{group}"
    candidate = directory / f"{base}.md"
    counter = 2
    while candidate.exists():
        candidate = directory / f"{base}-{counter}.md"
        counter += 1
    return candidate


def _sort_key(item: ScoredOpportunity) -> tuple[int, date]:
    deadline = item.opportunity.deadline or date.max
    return (-item.score, deadline)


def _deadline_cell(item: ScoredOpportunity, today: date) -> str:
    deadline = item.opportunity.deadline
    if deadline is None:
        return "–"
    days_left = (deadline - today).days
    unit = "Tag / day" if days_left == 1 else "Tage / days"
    return f"{deadline.isoformat()} ({days_left} {unit})"


def _escape_cell(text: str) -> str:
    return text.replace("|", "/").replace("\n", " ")


def _row(item: ScoredOpportunity, today: date) -> str:
    o = item.opportunity
    cells = [
        str(item.score),
        o.source,
        _escape_cell(o.title),
        _escape_cell(o.buyer),
        _deadline_cell(item, today),
        _escape_cell(o.amount_text or "–"),
        o.url,
    ]
    return "| " + " | ".join(cells) + " |"


def _opportunity_table(items: list[ScoredOpportunity], today: date) -> list[str]:
    header = [
        "| Punkte / Score | Quelle / Source | Titel / Title | Auftraggeber / Buyer"
        " | Frist / Deadline | Geld / Money | Link |",
        "|---|---|---|---|---|---|---|",
    ]
    return header + [_row(item, today) for item in sorted(items, key=_sort_key)]


def _new_section(digest: DigestInput) -> list[str]:
    lines = [f"## Neu seit dem letzten Lauf / New since the last run ({len(digest.new_items)})", ""]
    if not digest.new_items:
        return lines + ["Nichts Neues passt zu deinen Stichwörtern. / Nothing new matched your keywords.", ""]
    return lines + _opportunity_table(digest.new_items, digest.context.today) + [""]


def _closing_section(digest: DigestInput) -> list[str]:
    if not digest.closing_soon:
        return []
    lines = [
        (
            f"## Frist endet in {CLOSING_SOON_DAYS} Tagen (schon früher gemeldet) / "
            f"Closing within {CLOSING_SOON_DAYS} days (already reported earlier)"
        ),
        "",
    ]
    return lines + _opportunity_table(digest.closing_soon, digest.context.today) + [""]


def _counts_section(digest: DigestInput) -> list[str]:
    lines = []
    if digest.hidden_by_rules:
        lines.append(
            f"- {digest.hidden_by_rules} neue Einträge durch deine Ausschlussregeln ausgeblendet / "
            f"{digest.hidden_by_rules} new items were hidden by your exclusion rules."
        )
    if digest.unmatched_count:
        lines.append(
            f"- {digest.unmatched_count} neue Einträge ohne Stichwort-Treffer, nicht angezeigt / "
            f"{digest.unmatched_count} new items matched no keyword and are not shown."
        )
    return lines + [""] if lines else []


def _health_row(result: SourceResult) -> str:
    status = "ok" if result.succeeded else "FEHLER / FAILED"
    note = _escape_cell(result.error or "")
    return f"| {result.source} | {status} | {result.found_count} | {result.new_count} | {note} |"


def _health_section(digest: DigestInput) -> list[str]:
    header = [
        "## Zustand der Quellen / Source health",
        "",
        "| Quelle / Source | Status | Gefunden / Found | Neu / New | Hinweis / Note |",
        "|---|---|---|---|---|",
    ]
    return header + [_health_row(result) for result in digest.source_results] + [""]


def _manual_section(digest: DigestInput) -> list[str]:
    if not digest.manual_checks:
        return []
    lines = [
        "## Von Hand prüfen (der Radar kann diese nicht lesen) / Check by hand (the radar cannot read these)",
        "",
    ]
    for check in digest.manual_checks:
        suffix = f" ({check.note})" if check.note else ""
        lines.append(f"- {check.name}: {check.url}{suffix}")
    return lines + [""]


def _warning_section(digest: DigestInput) -> list[str]:
    if not digest.warnings:
        return []
    return ["## Warnungen / Warnings", ""] + [f"- {warning}" for warning in digest.warnings] + [""]


def render_digest(digest: DigestInput) -> str:
    header = [
        f"# Radar-Bericht / Radar digest {digest.context.today.isoformat()} ({digest.group})",
        "",
        f"Lauf-ID / Run id: `{digest.context.correlation_id}`",
        "",
    ]
    sections = (
        _new_section(digest)
        + _counts_section(digest)
        + _closing_section(digest)
        + _health_section(digest)
        + _manual_section(digest)
        + _warning_section(digest)
    )
    return "\n".join(header + sections)
