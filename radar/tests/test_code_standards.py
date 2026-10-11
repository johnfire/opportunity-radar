"""Enforces the house coding standards on this project's own code."""

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_FILES = sorted((PROJECT_ROOT / "src").rglob("*.py"))
TEST_FILES = sorted((PROJECT_ROOT / "tests").glob("*.py"))
ALL_FILES = SOURCE_FILES + TEST_FILES
BANNED_FILE_NAMES = {"utils.py", "helpers.py", "misc.py", "common.py", "stuff.py"}
MAX_FILE_LINES = 1000
MAX_FUNCTION_LINES = 40


def _function_lengths(path: Path) -> list[tuple[str, int]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    functions = (n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef))
    return [(f.name, (f.end_lineno or f.lineno) - f.lineno + 1) for f in functions]


def test_no_generic_file_names() -> None:
    assert [p.name for p in ALL_FILES if p.name in BANNED_FILE_NAMES] == []


def test_no_file_is_longer_than_the_limit() -> None:
    too_long = [p.name for p in ALL_FILES if len(p.read_text(encoding="utf-8").splitlines()) > MAX_FILE_LINES]
    assert too_long == []


def test_no_function_is_longer_than_the_limit() -> None:
    too_long = [
        f"{path.name}:{name} ({length} lines)"
        for path in ALL_FILES
        for name, length in _function_lengths(path)
        if length > MAX_FUNCTION_LINES
    ]
    assert too_long == []
