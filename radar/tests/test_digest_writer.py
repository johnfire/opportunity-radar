from datetime import date
from pathlib import Path

from radar.digest_writer import (
    DigestInput,
    ManualCheck,
    SourceResult,
    next_digest_path,
    parse_manual_check_lines,
    render_digest,
)
from radar.jev_fit_scoring import FitJudgment
from radar.keyword_scoring import ScoredOpportunity
from radar.opportunity_model import Opportunity, RunContext

TODAY = date(2026, 10, 11)


def scored(
    title: str, score: int, deadline: date | None, source: str = "ted", amount: str | None = None
) -> ScoredOpportunity:
    opportunity = Opportunity(source, title, title, "Buyer GmbH", f"https://x/{title}", deadline, amount, "")
    return ScoredOpportunity(opportunity, score, ("software",) if score else (), ())


def a_digest_input(**overrides: object) -> DigestInput:
    fields: dict[str, object] = {
        "context": RunContext("run-42", TODAY),
        "group": "weekly",
        "new_items": [],
        "closing_soon": [],
        "hidden_by_rules": 0,
        "unmatched_count": 0,
        "source_results": [SourceResult("ted", True, 10, 2, None)],
        "manual_checks": [],
        "warnings": [],
    }
    fields.update(overrides)
    return DigestInput(**fields)  # type: ignore[arg-type]


def test_header_names_the_date_group_and_run_id() -> None:
    text = render_digest(a_digest_input())
    assert text.startswith("# Radar-Bericht / Radar digest 2026-10-11 (weekly)")
    assert "run-42" in text


def test_new_items_are_sorted_by_score_then_earliest_deadline() -> None:
    items = [
        scored("low", 1, date(2026, 11, 1)),
        scored("high-late", 5, date(2026, 12, 1)),
        scored("high-early", 5, date(2026, 11, 5)),
    ]
    text = render_digest(a_digest_input(new_items=items))
    assert text.index("high-early") < text.index("high-late") < text.index("low")


def test_a_row_shows_deadline_days_left_amount_and_link() -> None:
    items = [scored("Datenplattform", 3, date(2026, 10, 21), amount="Budget laut Portal: 5.000.000 €")]
    text = render_digest(a_digest_input(new_items=items))
    assert "2026-10-21 (10 Tage / days)" in text
    assert "Budget laut Portal: 5.000.000 €" in text
    assert "https://x/Datenplattform" in text


def test_one_day_left_is_written_in_the_singular() -> None:
    text = render_digest(a_digest_input(new_items=[scored("Tomorrow", 2, date(2026, 10, 12))]))
    assert "(1 Tag / day)" in text and "(1 Tage / days)" not in text


def test_an_item_without_deadline_is_shown_with_a_dash() -> None:
    text = render_digest(a_digest_input(new_items=[scored("Rolling", 2, None)]))
    assert "| – |" in text


def test_nothing_new_is_stated_plainly() -> None:
    text = render_digest(a_digest_input())
    assert "Nichts Neues passt zu deinen Stichwörtern. / Nothing new matched your keywords." in text


def test_closing_soon_section_lists_known_items_with_their_days_left() -> None:
    text = render_digest(a_digest_input(closing_soon=[scored("Almost over", 2, date(2026, 10, 14))]))
    assert "Closing within 14 days (already reported earlier)" in text
    assert "Almost over" in text and "(3 Tage / days)" in text


def test_counts_of_hidden_and_unmatched_items_are_reported() -> None:
    text = render_digest(a_digest_input(hidden_by_rules=7, unmatched_count=40))
    assert "7 new items were hidden by your exclusion rules." in text
    assert "40 new items matched no keyword" in text


def test_failed_source_is_shown_with_its_reason() -> None:
    results = [SourceResult("ted", True, 10, 2, None), SourceResult("eu_portal", False, 0, 0, "HTTP 500")]
    text = render_digest(a_digest_input(source_results=results))
    assert "| ted | ok | 10 | 2 |" in text
    assert "| eu_portal | FEHLER / FAILED | 0 | 0 | HTTP 500 |" in text


def test_manual_checks_and_warnings_are_listed() -> None:
    text = render_digest(
        a_digest_input(
            manual_checks=[ManualCheck("ZIM", "https://zim.de", "blocked for bots")],
            warnings=["seen-state file was corrupt"],
        )
    )
    assert "- ZIM: https://zim.de (blocked for bots)" in text
    assert "seen-state file was corrupt" in text


def test_manual_check_lines_are_parsed() -> None:
    parsed = parse_manual_check_lines("# c\nZIM | https://zim.de | blocked\n\nDTVP | https://dtvp.de |\n")
    assert parsed == [
        ManualCheck("ZIM", "https://zim.de", "blocked"),
        ManualCheck("DTVP", "https://dtvp.de", ""),
    ]


def test_digest_path_is_dated_and_never_overwrites(tmp_path: Path) -> None:
    first = next_digest_path(tmp_path, TODAY, "weekly")
    assert first.name == "2026-10-11-weekly.md"
    first.write_text("x", encoding="utf-8")
    assert next_digest_path(tmp_path, TODAY, "weekly").name == "2026-10-11-weekly-2.md"


def test_every_heading_is_written_in_german_and_english() -> None:
    manual = [ManualCheck("ZIM", "https://www.zim.de", "")]
    text = render_digest(a_digest_input(new_items=[scored("x", 3, None)], manual_checks=manual))
    for heading in (
        "## Neu seit dem letzten Lauf / New since the last run",
        "## Zustand der Quellen / Source health",
        "## Von Hand prüfen (der Radar kann diese nicht lesen) / Check by hand",
    ):
        assert heading in text


def test_with_jev_answers_the_most_solvable_item_comes_first_and_unjudged_items_last() -> None:
    items = [
        scored("high-keyword-low-fit", 9, date(2026, 11, 1)),
        scored("low-keyword-high-fit", 1, date(2026, 11, 1)),
        scored("not-judged", 20, date(2026, 11, 1)),
    ]
    fits = {
        "ted:high-keyword-low-fit": FitJudgment(0.2, "service_tender"),
        "ted:low-keyword-high-fit": FitJudgment(0.8, "service_tender"),
    }
    text = render_digest(a_digest_input(new_items=items, fits=fits))
    assert text.index("low-keyword-high-fit") < text.index("high-keyword-low-fit") < text.index("not-judged")
    assert "Sorted by Jev probability" in text
