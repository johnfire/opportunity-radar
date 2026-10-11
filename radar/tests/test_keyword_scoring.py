from datetime import date

from radar.keyword_scoring import (
    KeywordWeight,
    parse_exclusion_lines,
    parse_keyword_lines,
    score_opportunity,
)
from radar.opportunity_model import Opportunity


def an_opportunity(title: str, summary: str = "") -> Opportunity:
    return Opportunity("ted", "1", title, "Buyer", "https://x", date(2026, 11, 1), None, summary)


def test_keyword_lines_support_comments_blank_lines_and_weights() -> None:
    text = "# comment\n\nsoftware\ndaten | 2\n  KI  | 3 \n"
    assert parse_keyword_lines(text) == (
        KeywordWeight("software", 1),
        KeywordWeight("daten", 2),
        KeywordWeight("ki", 3),
    )


def test_exclusion_lines_ignore_comments_and_blank_lines() -> None:
    assert parse_exclusion_lines("# x\nLizenz\n\n Reinigung \n") == ("lizenz", "reinigung")


def test_score_adds_the_weights_of_every_matching_keyword() -> None:
    keywords = (KeywordWeight("software", 1), KeywordWeight("daten", 2), KeywordWeight("bau", 5))
    scored = score_opportunity(an_opportunity("Software für Daten"), keywords, ())
    assert scored.score == 3
    assert scored.matched_keywords == ("software", "daten")


def test_matching_ignores_case_and_looks_in_the_summary_too() -> None:
    keywords = (KeywordWeight("daten", 2),)
    scored = score_opportunity(an_opportunity("Neues Projekt", "Eine DATENplattform entsteht"), keywords, ())
    assert scored.score == 2


def test_a_long_keyword_matches_at_the_start_of_a_word_including_compounds() -> None:
    keywords = (KeywordWeight("software", 1),)
    assert score_opportunity(an_opportunity("Softwareentwicklung"), keywords, ()).score == 1
    assert score_opportunity(an_opportunity("Open-Source-Software"), keywords, ()).score == 1


def test_a_long_keyword_does_not_match_inside_a_word() -> None:
    keywords = (KeywordWeight("daten", 1),)
    assert score_opportunity(an_opportunity("Metadaten und Updaten"), keywords, ()).score == 0


def test_a_short_keyword_matches_only_as_a_whole_word() -> None:
    keywords = (KeywordWeight("ki", 3), KeywordWeight("app", 2))
    assert score_opportunity(an_opportunity("Kinderwarnwesten und Apparate"), keywords, ()).score == 0
    assert score_opportunity(an_opportunity("Einsatz von KI und App-Entwicklung"), keywords, ()).score == 5


def test_an_exclusion_marks_the_opportunity_and_zeroes_its_score() -> None:
    keywords = (KeywordWeight("software", 1),)
    scored = score_opportunity(an_opportunity("Software Lizenzen verlängern"), keywords, ("lizenz",))
    assert scored.is_excluded is True
    assert scored.excluded_by == ("lizenz",)
    assert scored.score == 0


def test_no_match_gives_score_zero_and_is_not_excluded() -> None:
    scored = score_opportunity(an_opportunity("Straßenreinigung"), (KeywordWeight("software", 1),), ())
    assert scored.score == 0
    assert scored.is_excluded is False
