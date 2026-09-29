import pytest

from tests.support import SAMPLE, run_csv


@pytest.fixture
def sample():
    return run_csv(SAMPLE.read_text(encoding="utf-8"))
