from datetime import date

import pytest

from radar.opportunity_model import Opportunity, RunContext


def make_opportunity(**overrides: object) -> Opportunity:
    fields: dict[str, object] = {
        "source": "koinno",
        "source_id": "abc123",
        "title": "Beihilfe-App",
        "buyer": "LBV",
        "url": "https://example.org/abc123",
        "deadline": date(2026, 10, 12),
        "amount_text": None,
        "summary": "Replacement app",
    }
    fields.update(overrides)
    return Opportunity(**fields)  # type: ignore[arg-type]


def test_key_combines_source_and_source_id() -> None:
    assert make_opportunity().key == "koinno:abc123"


def test_opportunity_is_immutable() -> None:
    opportunity = make_opportunity()
    with pytest.raises(AttributeError):
        opportunity.title = "changed"  # type: ignore[misc]


def test_days_until_deadline_counts_from_today() -> None:
    opportunity = make_opportunity(deadline=date(2026, 10, 12))
    assert opportunity.days_until_deadline(date(2026, 10, 10)) == 2


def test_days_until_deadline_is_none_without_deadline() -> None:
    assert make_opportunity(deadline=None).days_until_deadline(date(2026, 10, 10)) is None


def test_run_context_carries_correlation_id_and_today() -> None:
    context = RunContext(correlation_id="run-1", today=date(2026, 10, 11))
    assert context.correlation_id == "run-1"
    assert context.today == date(2026, 10, 11)
