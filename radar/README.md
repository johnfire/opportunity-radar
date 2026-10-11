# Opportunity radar

Checks public funding and tender sources on a schedule and writes a markdown digest of what is **new**,
what is **closing within 14 days**, and which sources **failed**. It never submits anything.

## Jev fit scoring (optional)
If `~/.config/typesafe/jev.env` holds `TYPESAFE_API_KEY=...`, every shown item is sent (title, buyer, a short summary only) to
TypeSafe's Jev, which returns the probability that a very small software and AI team could solve the need, and what kind of
offer it is. The result is the "Jev: lösbar? / solvable?" column. It never hides or reorders items. Without the key file the
radar runs exactly as before. Set `RADAR_JEV_ENV_FILE` to use another file. If Jev fails, the digest is still written
with a warning. Each run logs a `jev_fit_scoring` entry in the audit log.

## Run it
```bash
.venv/bin/radar run --group weekly          # KOINNO, EU portal, TED
.venv/bin/radar run --group twice-monthly   # BMFTR announcements, service.bund.de
```
Output: `digests/YYYY-MM-DD-<group>.md` (never overwritten; a second run on the same day gets `-2`),
`state/seen.json` (what was already reported), `audit/audit.jsonl` (append-only record of every action).
A desktop notification (`notify-send`) summarises the run.

## Schedule (systemd user timers, catch-up if the laptop was off)
| Group | When | Sources |
|---|---|---|
| weekly | Saturday 08:00 | koinno, eu_portal, ted |
| twice-monthly | 1st and 15th, 08:00 | bmftr, service_bund, sprind (Prototype Fund is behind a bot check, so it is on the check-by-hand list) |

```bash
systemd/install_timers.sh                   # weekly only
systemd/install_timers.sh weekly twice-monthly
systemd/uninstall_timers.sh                 # removes everything it installed
```

## Tune it
Plain text files in `config/`, re-read on every run:
- `keywords.txt` — what you want to see (`term | weight`); short terms match whole words, longer ones at the start of a word
- `exclusions.txt` — anything containing these words is hidden and only counted
- `manual_checks.txt` — sources the radar cannot read; listed in every digest as a reminder

KOINNOvationsplatz is a small curated list, so it shows **every** new challenge, not only keyword matches.

## Design (house standards)
- One module per source in `src/radar/sources/`; each source runs in its own try/except, so one broken site never stops the others.
- All network access goes through `http_transport.py`; tests inject captured real responses from `fixtures/`.
- Every run has a correlation id; every fetch and digest write is in the audit log with actor `radar-bot`.
- State is only saved after the digest was written; a corrupt state file is set aside, never deleted.
- `tests/test_code_standards.py` enforces: no generic file names, files ≤ 1000 lines, functions ≤ 40 lines.

## Develop
```bash
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
.venv/bin/pytest -q                 # unit, integration, end to end, standards
.venv/bin/ruff check . && .venv/bin/ruff format --check . && .venv/bin/mypy src tests
RADAR_NETWORK_TESTS=1 .venv/bin/pytest -m network   # live smoke tests, opt-in
```
CI (`.github/workflows/radar-ci.yml`) runs lint, strict type check, tests and `pip-audit` on every push.

## Add a source
1. Capture a real response into `fixtures/`, strip personal data.
2. Write the test in `tests/test_<name>_source.py`.
3. Implement `fetch_<name>_opportunities(transport, context) -> list[Opportunity]` in `src/radar/sources/<name>_source.py`.
4. Register it in `source_registry.py` and add it to a group.
