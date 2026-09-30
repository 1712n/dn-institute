import sys
from pathlib import Path

# The tool is a pair of plain modules, not an installed package.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
