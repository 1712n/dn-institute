# Informed trading on Polymarket

Submission for issue #1222. The write-up is in `REPORT.md`.

- `code/`: the pipeline, tests and hand-built inputs; `code/README.md` lists every step.
- `data/`: the CSV outputs the write-up quotes.
- `data/tape/`: every collected market and trade (15,604 markets, 13.2M trades) as Parquet files, the input of the whole analysis.
- `figures/`: the figures of the write-up, drawn by `code/make_figures.py`.

To reproduce, run from `code/`: `python build_db.py`, then the five steps listed in `code/README.md`. The outputs match `data/` and `figures/` byte for byte.
