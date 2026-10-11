"""One radar run: fetch every source in isolation, score, write the digest, remember, notify."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from radar.audit_log import ACTOR_NAME, AuditEntry, append_audit_entry
from radar.digest_writer import (
    CLOSING_SOON_DAYS,
    DigestInput,
    ManualCheck,
    SourceResult,
    next_digest_path,
    parse_manual_check_lines,
    render_digest,
)
from radar.http_transport import Transport
from radar.jev_fit_scoring import FitJudgment
from radar.keyword_scoring import (
    KeywordWeight,
    ScoredOpportunity,
    parse_exclusion_lines,
    parse_keyword_lines,
    score_opportunity,
)
from radar.opportunity_model import Opportunity, RunContext
from radar.seen_state_store import (
    SeenState,
    load_seen_state,
    partition_new_and_known,
    save_seen_state,
    update_seen_state,
)
from radar.source_registry import SourceDefinition

Notifier = Callable[[str, str], bool]
FitJudge = Callable[[list[Opportunity]], tuple[dict[str, FitJudgment], list[str]]]


class DigestWriteError(Exception):
    """The digest could not be written; nothing was marked as seen."""


@dataclass(frozen=True)
class RadarPaths:
    root: Path

    @property
    def state_file(self) -> Path:
        return self.root / "state" / "seen.json"

    @property
    def digest_directory(self) -> Path:
        return self.root / "digests"

    @property
    def audit_file(self) -> Path:
        return self.root / "audit" / "audit.jsonl"

    @property
    def keywords_file(self) -> Path:
        return self.root / "config" / "keywords.txt"

    @property
    def exclusions_file(self) -> Path:
        return self.root / "config" / "exclusions.txt"

    @property
    def manual_checks_file(self) -> Path:
        return self.root / "config" / "manual_checks.txt"


@dataclass(frozen=True)
class RunReport:
    digest_path: Path
    new_count: int
    shown_count: int
    failed_sources: list[str]


def _audit(
    paths: RadarPaths, context: RunContext, action: str, target: str, outcome: str, detail: str
) -> None:
    entry = AuditEntry(
        timestamp=datetime.now(UTC).astimezone().isoformat(timespec="seconds"),
        correlation_id=context.correlation_id,
        actor=ACTOR_NAME,
        action=action,
        target=target,
        outcome=outcome,
        detail=detail,
    )
    append_audit_entry(paths.audit_file, entry)


def _fetch_one(
    source: SourceDefinition, transport: Transport, context: RunContext, paths: RadarPaths
) -> tuple[list[Opportunity], str | None]:
    try:
        found = source.fetch(transport, context)
    except Exception as error:  # noqa: BLE001 - one source's failure must never stop the others
        message = str(error) or repr(error)
        _audit(paths, context, "fetch_source", source.name, "failed", message)
        return [], message
    _audit(paths, context, "fetch_source", source.name, "ok", f"{len(found)} opportunities")
    return found, None


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _load_scoring_rules(paths: RadarPaths) -> tuple[tuple[KeywordWeight, ...], tuple[str, ...], list[str]]:
    warnings: list[str] = []
    keyword_text = _read_text(paths.keywords_file)
    if keyword_text is None:
        warnings.append("keyword file could not be read; showing every new item unscored")
    exclusion_text = _read_text(paths.exclusions_file)
    if exclusion_text is None:
        warnings.append("exclusion file could not be read; no exclusion rules applied")
    keywords = parse_keyword_lines(keyword_text or "")
    exclusions = parse_exclusion_lines(exclusion_text or "")
    return keywords, exclusions, warnings


def _load_manual_checks(paths: RadarPaths) -> list[ManualCheck]:
    text = _read_text(paths.manual_checks_file)
    return parse_manual_check_lines(text) if text else []


def _is_shown(item: ScoredOpportunity, minimum_score: int, curated_sources: frozenset[str]) -> bool:
    if item.is_excluded:
        return False
    return item.score >= minimum_score or item.opportunity.source in curated_sources


def _is_closing_soon(item: ScoredOpportunity, context: RunContext) -> bool:
    days_left = item.opportunity.days_until_deadline(context.today)
    return not item.is_excluded and days_left is not None and 0 <= days_left <= CLOSING_SOON_DAYS


def _closing_soon(known: list[ScoredOpportunity], context: RunContext) -> list[ScoredOpportunity]:
    return [item for item in known if _is_closing_soon(item, context)]


def _write_digest(text: str, paths: RadarPaths, context: RunContext, group: str) -> Path:
    try:
        paths.digest_directory.mkdir(parents=True, exist_ok=True)
        path = next_digest_path(paths.digest_directory, context.today, group)
        path.write_text(text, encoding="utf-8")
    except OSError as error:
        _audit(paths, context, "write_digest", str(paths.digest_directory), "failed", str(error))
        raise DigestWriteError(str(error)) from error
    _audit(paths, context, "write_digest", str(path.name), "ok", f"{len(text)} characters")
    return path


def _summary_message(new_count: int, shown_count: int, failed: list[str]) -> str:
    message = f"{shown_count} of {new_count} new opportunities match your keywords"
    if failed:
        message += f" - failed: {', '.join(failed)}"
    return message


@dataclass(frozen=True)
class Findings:
    results: list[SourceResult]
    new: list[Opportunity]
    known: list[Opportunity]
    show_everything_from: frozenset[str]


def _gather_findings(
    sources: list[SourceDefinition],
    transport: Transport,
    context: RunContext,
    paths: RadarPaths,
    state: SeenState,
) -> Findings:
    results: list[SourceResult] = []
    all_new: list[Opportunity] = []
    all_known: list[Opportunity] = []
    for source in sources:
        found, error = _fetch_one(source, transport, context, paths)
        new, known = partition_new_and_known(found, state)
        all_new.extend(new)
        all_known.extend(known)
        results.append(SourceResult(source.name, error is None, len(found), len(new), error))
    curated = frozenset(source.name for source in sources if source.shows_everything_new)
    return Findings(results, all_new, all_known, curated)


def _judge_fit_safely(
    fit_judge: FitJudge | None, shown: list[ScoredOpportunity], paths: RadarPaths, context: RunContext
) -> tuple[dict[str, FitJudgment], list[str]]:
    """Advisory step: whatever goes wrong here, the digest is still written."""
    if fit_judge is None or not shown:
        return {}, []
    try:
        fits, warnings = fit_judge([item.opportunity for item in shown])
    except Exception as error:  # noqa: BLE001 - the digest must survive any failure of this optional step
        _audit(paths, context, "jev_fit_scoring", "jev", "failed", repr(error))
        return {}, [f"Jev scoring was skipped ({error!r}). / Jev-Bewertung übersprungen."]
    _audit(paths, context, "jev_fit_scoring", "jev", "ok", f"{len(fits)} of {len(shown)} items judged")
    return fits, warnings


def _assemble_digest(
    group: str,
    context: RunContext,
    findings: Findings,
    paths: RadarPaths,
    warnings: list[str],
    fit_judge: FitJudge | None = None,
) -> tuple[DigestInput, int]:
    keywords, exclusions, rule_warnings = _load_scoring_rules(paths)
    new_scored = [score_opportunity(o, keywords, exclusions) for o in findings.new]
    known_scored = [score_opportunity(o, keywords, exclusions) for o in findings.known]
    minimum_score = 1 if keywords else 0
    shown = [s for s in new_scored if _is_shown(s, minimum_score, findings.show_everything_from)]
    fits, fit_warnings = _judge_fit_safely(fit_judge, shown, paths, context)
    digest = DigestInput(
        context=context,
        group=group,
        new_items=shown,
        closing_soon=_closing_soon(known_scored, context),
        hidden_by_rules=sum(1 for s in new_scored if s.is_excluded),
        unmatched_count=sum(1 for s in new_scored if not s.is_excluded and s not in shown),
        source_results=findings.results,
        manual_checks=_load_manual_checks(paths),
        warnings=warnings + rule_warnings + fit_warnings,
        fits=fits,
    )
    return digest, len(shown)


def run_radar(
    group: str,
    transport: Transport,
    context: RunContext,
    paths: RadarPaths,
    notifier: Notifier,
    sources: list[SourceDefinition],
    fit_judge: FitJudge | None = None,
) -> RunReport:
    state, state_warning = load_seen_state(paths.state_file)
    findings = _gather_findings(sources, transport, context, paths, state)
    digest, shown_count = _assemble_digest(
        group, context, findings, paths, [state_warning] if state_warning else [], fit_judge
    )
    digest_path = _write_digest(render_digest(digest), paths, context, group)
    save_seen_state(update_seen_state(state, findings.new + findings.known, context.today), paths.state_file)
    failed = [r.source for r in findings.results if not r.succeeded]
    notifier("Opportunity radar", _summary_message(len(findings.new), shown_count, failed))
    return RunReport(digest_path, len(findings.new), shown_count, failed)
