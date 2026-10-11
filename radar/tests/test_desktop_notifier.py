import subprocess

from radar.desktop_notifier import notify_desktop


def test_calls_notify_send_with_title_and_message() -> None:
    calls: list[list[str]] = []

    def fake_runner(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    assert notify_desktop("Radar", "3 new opportunities", runner=fake_runner) is True
    assert calls == [["notify-send", "--app-name=opportunity-radar", "Radar", "3 new opportunities"]]


def test_missing_notify_send_is_reported_not_raised() -> None:
    def missing(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        raise FileNotFoundError("notify-send")

    assert notify_desktop("Radar", "x", runner=missing) is False


def test_nonzero_exit_is_reported_not_raised() -> None:
    def failing(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, 1)

    assert notify_desktop("Radar", "x", runner=failing) is False
