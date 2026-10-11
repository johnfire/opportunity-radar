"""Turns a run's findings into the markdown digest Chris reads."""

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from radar.jev_fit_scoring import FitJudgment
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
    fits: dict[str, FitJudgment] = field(default_factory=dict)


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


NO_FIT_RANK = 1.0  # items Jev did not judge sort after every judged item


def _sort_key(item: ScoredOpportunity, fits: dict[str, FitJudgment]) -> tuple[float, int, date]:
    """Most solvable first (Jev), then keyword score, then earliest deadline."""
    fit = fits.get(item.opportunity.key)
    solvable_rank = -fit.could_solve if fit else NO_FIT_RANK
    return (solvable_rank, -item.score, item.opportunity.deadline or date.max)


def _deadline_cell(item: ScoredOpportunity, today: date) -> str:
    deadline = item.opportunity.deadline
    if deadline is None:
        return "–"
    days_left = (deadline - today).days
    unit = "Tag / day" if days_left == 1 else "Tage / days"
    return f"{deadline.isoformat()} ({days_left} {unit})"


def _escape_cell(text: str) -> str:
    return text.replace("|", "/").replace("\n", " ")


CALL_KIND_LABELS = {
    "funding_or_research_call": "Förderung / grant",
    "service_tender": "Dienstleistung / service tender",
    "goods_or_licence_purchase": "Ware, Lizenz / goods, licence",
    "other": "Sonstiges / other",
}


def _fit_cell(item: ScoredOpportunity, fits: dict[str, FitJudgment]) -> str:
    fit = fits.get(item.opportunity.key)
    if fit is None:
        return "–"
    return f"{round(fit.could_solve * 100)} % · {CALL_KIND_LABELS.get(fit.call_kind, fit.call_kind)}"


def _row(item: ScoredOpportunity, today: date, fits: dict[str, FitJudgment]) -> str:
    o = item.opportunity
    cells = [
        str(item.score),
        o.source,
        _escape_cell(o.title),
        _escape_cell(o.buyer),
        _deadline_cell(item, today),
        _escape_cell(o.amount_text or "–"),
    ]
    if fits:
        cells.append(_fit_cell(item, fits))
    return "| " + " | ".join(cells + [o.url]) + " |"


def _opportunity_table(
    items: list[ScoredOpportunity], today: date, fits: dict[str, FitJudgment]
) -> list[str]:
    columns = [
        "Punkte / Score",
        "Quelle / Source",
        "Titel / Title",
        "Auftraggeber / Buyer",
        "Frist / Deadline",
        "Geld / Money",
    ]
    if fits:
        columns.append("Jev: lösbar? / solvable?")
    header = ["| " + " | ".join(columns + ["Link"]) + " |", "|" + "---|" * (len(columns) + 1)]
    return header + [
        _row(item, today, fits) for item in sorted(items, key=lambda item: _sort_key(item, fits))
    ]


def _new_section(digest: DigestInput) -> list[str]:
    lines = [f"## Neu seit dem letzten Lauf / New since the last run ({len(digest.new_items)})", ""]
    if not digest.new_items:
        return lines + ["Nichts Neues passt zu deinen Stichwörtern. / Nothing new matched your keywords.", ""]
    if digest.fits:
        lines += [
            "Sortiert nach Jev-Wahrscheinlichkeit, dann Punkte / Sorted by Jev probability, then score.",
            "",
        ]
    return lines + _opportunity_table(digest.new_items, digest.context.today, digest.fits) + [""]


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
    return lines + _opportunity_table(digest.closing_soon, digest.context.today, digest.fits) + [""]


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
