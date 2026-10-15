import hashlib
import re

import pytest

import config
import make_figures

POST_DIR = config.ROOT.parent if (config.ROOT.parent / "index.md").exists() else None


def _figures(out):
    return out / "figures"


def test_every_declared_figure_is_rendered(pipeline_out):
    names = {f.name for f in _figures(pipeline_out).glob("*.png")}
    assert names == set(make_figures.FIGURES), names ^ set(make_figures.FIGURES)
    for n in names:
        assert (_figures(pipeline_out) / n).stat().st_size > 10_000, n


def test_figures_are_reproducible(pipeline_out, pipeline_out_repeat):
    for n in make_figures.FIGURES:
        a = hashlib.sha256((_figures(pipeline_out) / n).read_bytes()).hexdigest()
        b = hashlib.sha256((_figures(pipeline_out_repeat) / n).read_bytes()).hexdigest()
        assert a == b, n


@pytest.mark.skipif(POST_DIR is None, reason="runs inside the published post bundle only")
def test_post_figures_match_generator():
    referenced = set(re.findall(r'src="([^"]+\.png)"', (POST_DIR / "index.md").read_text("utf-8")))
    on_disk = {p.name for p in POST_DIR.glob("*.png")}
    assert referenced == on_disk == set(make_figures.FIGURES)


@pytest.mark.skipif(POST_DIR is None, reason="runs inside the published post bundle only")
def test_post_data_is_generated_by_pipeline(pipeline_out):
    committed = {p.name for p in (POST_DIR / "data").glob("*.csv")}
    generated = {p.name for p in pipeline_out.glob("*.csv")}
    assert committed <= generated, committed - generated
