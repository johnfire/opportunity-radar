"""Desktop pop-up when a run finishes. A missing or failing notifier never stops the radar."""

import subprocess
from collections.abc import Callable
from typing import Any

Runner = Callable[..., "subprocess.CompletedProcess[Any]"]


def notify_desktop(title: str, message: str, runner: Runner = subprocess.run) -> bool:
    command = ["notify-send", "--app-name=opportunity-radar", title, message]
    try:
        completed = runner(command, check=False, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return False
    return completed.returncode == 0
