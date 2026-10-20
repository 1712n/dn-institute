import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [*ROOT.glob("*.py"), *ROOT.glob("src/*.py"), *ROOT.glob("tests/*.py")]


def _imported():
    names = set()
    for path in SOURCES:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                names |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                names.add(node.module.split(".")[0])
    return names


def _local():
    return {p.stem for p in SOURCES} | {"src"}


def _required():
    lines = (ROOT / "requirements.txt").read_text().splitlines()
    return {re.split(r"[<>=~!\[ ]", line.strip())[0].lower() for line in lines if line.strip()}


def test_every_third_party_import_is_required():
    third_party = _imported() - set(sys.stdlib_module_names) - _local()
    assert sorted(third_party - _required()) == []


def test_scan_sees_the_plotting_and_test_imports():
    # guards the test itself: if the scan finds nothing it passes for the wrong reason
    assert {"matplotlib", "pytest", "duckdb", "pandas"} <= _imported()
