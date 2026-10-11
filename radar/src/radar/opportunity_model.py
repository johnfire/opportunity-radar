"""The shared shape every source turns its findings into."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Opportunity:
    source: str
    source_id: str
    title: str
    buyer: str
    url: str
    deadline: date | None
    amount_text: str | None
    summary: str

    @property
    def key(self) -> str:
        return f"{self.source}:{self.source_id}"

    def days_until_deadline(self, today: date) -> int | None:
        if self.deadline is None:
            return None
        return (self.deadline - today).days


@dataclass(frozen=True)
class RunContext:
    """Identifies one run so every log line and audit entry can be traced back to it."""

    correlation_id: str
    today: date
