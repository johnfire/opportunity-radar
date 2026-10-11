"""Command line entry point: `radar run --group weekly`."""

import argparse
import os
import sys
import uuid
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from radar.desktop_notifier import notify_desktop
from radar.http_transport import Transport, fetch_over_network
from radar.opportunity_model import RunContext
from radar.radar_run_orchestrator import DigestWriteError, Notifier, RadarPaths, run_radar
from radar.source_registry import GROUPS, sources_for_group

EXIT_OK = 0
EXIT_DIGEST_NOT_WRITTEN = 2
EXIT_UNKNOWN_GROUP = 3


def _default_root() -> Path:
    from_environment = os.environ.get("RADAR_ROOT")
    return Path(from_environment) if from_environment else Path(__file__).resolve().parents[2]


def _parse_arguments(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="radar", description="Opportunity radar")
    commands = parser.add_subparsers(dest="command", required=True)
    run_command = commands.add_parser("run", help="check the sources of one schedule group")
    run_command.add_argument("--group", required=True, help=f"one of: {', '.join(sorted(GROUPS))}")
    run_command.add_argument(
        "--root", type=Path, default=_default_root(), help="folder holding config, state, digests"
    )
    return parser.parse_args(argv)


def main(
    argv: Sequence[str] | None = None,
    transport: Transport = fetch_over_network,
    notifier: Notifier = notify_desktop,
) -> int:
    arguments = _parse_arguments(argv)
    try:
        sources = sources_for_group(arguments.group)
    except ValueError as error:
        print(error, file=sys.stderr)
        return EXIT_UNKNOWN_GROUP
    context = RunContext(correlation_id=uuid.uuid4().hex[:12], today=date.today())
    try:
        report = run_radar(arguments.group, transport, context, RadarPaths(arguments.root), notifier, sources)
    except DigestWriteError as error:
        print(f"digest could not be written: {error}", file=sys.stderr)
        return EXIT_DIGEST_NOT_WRITTEN
    print(f"{report.digest_path} ({report.shown_count} shown of {report.new_count} new)")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
