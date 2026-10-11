"""Rank opportunities by how well their text matches Chris's keyword list (plain text files, editable)."""

import re
from dataclasses import dataclass

from radar.opportunity_model import Opportunity


@dataclass(frozen=True)
class KeywordWeight:
    term: str
    weight: int


@dataclass(frozen=True)
class ScoredOpportunity:
    opportunity: Opportunity
    score: int
    matched_keywords: tuple[str, ...]
    excluded_by: tuple[str, ...]

    @property
    def is_excluded(self) -> bool:
        return bool(self.excluded_by)


def _content_lines(text: str) -> list[str]:
    stripped = (line.strip() for line in text.splitlines())
    return [line for line in stripped if line and not line.startswith("#")]


def _parse_weighted_line(line: str) -> KeywordWeight:
    term, _, weight_text = line.partition("|")
    weight = int(weight_text.strip()) if weight_text.strip() else 1
    return KeywordWeight(term.strip().lower(), weight)


def parse_keyword_lines(text: str) -> tuple[KeywordWeight, ...]:
    return tuple(_parse_weighted_line(line) for line in _content_lines(text))


def parse_exclusion_lines(text: str) -> tuple[str, ...]:
    return tuple(line.lower() for line in _content_lines(text))


SHORT_TERM_LENGTH = 3


def _matches(term: str, text: str) -> bool:
    """Short terms ('ki', 'app') must be whole words; longer terms may start a compound word."""
    escaped = re.escape(term)
    pattern = rf"(?<!\w){escaped}(?!\w)" if len(term) <= SHORT_TERM_LENGTH else rf"(?<!\w){escaped}"
    return re.search(pattern, text) is not None


def score_opportunity(
    opportunity: Opportunity,
    keywords: tuple[KeywordWeight, ...],
    exclusions: tuple[str, ...],
) -> ScoredOpportunity:
    haystack = f"{opportunity.title} {opportunity.summary}".lower()
    excluded_by = tuple(term for term in exclusions if term in haystack)
    if excluded_by:
        return ScoredOpportunity(opportunity, 0, (), excluded_by)
    matching = [k for k in keywords if _matches(k.term, haystack)]
    return ScoredOpportunity(
        opportunity, sum(k.weight for k in matching), tuple(k.term for k in matching), ()
    )
