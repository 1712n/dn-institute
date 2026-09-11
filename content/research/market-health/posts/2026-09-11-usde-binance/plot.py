#!/usr/bin/env python3
"""Generate research figures from analyze.py outputs; no network access."""

import csv
import datetime as dt
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np


ROOT = Path(__file__).resolve().parent
UTC = dt.timezone.utc
BLUE, ORANGE, GREEN = "#245d8b", "#bd6626", "#28775b"


def read(name):
    with (ROOT / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def date(value):
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def time_axis(ax):
    ax.set_xlim(date("2025-10-10T21:00:00Z"), date("2025-10-10T23:00:00Z"))
    ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=[0, 20, 40], tz=UTC))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=UTC))


def shade_official(ax):
    ax.axvspan(date("2025-10-10T21:36:00Z"), date("2025-10-10T22:16:00Z"), color="#626c76", alpha=0.08)


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.titlesize": 13, "axes.labelsize": 11,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.grid": True, "grid.color": "#dee3e7", "grid.linewidth": 0.6,
                         "axes.axisbelow": True, "savefig.facecolor": "white"})
    all_minutes = read("minute_metrics.csv")
    minutes = [r for r in all_minutes if r["symbol"] == "USDEUSDT"
               and r["minute_utc"].startswith("2025-10-10")]
    minute_map = {date(r["minute_utc"]): r for r in minutes}
    quotes = {date(r["minute_utc"]): r for r in read("quote_comparison.csv")}
    times = [date("2025-10-10T21:00:00Z") + dt.timedelta(minutes=i) for i in range(120)]
    values = lambda field: [float(minute_map[t][field]) if t in minute_map else np.nan for t in times]
    quote_values = lambda field: [float(quotes[t][field]) if t in quotes else np.nan for t in times]
    fig, axes = plt.subplots(2, 1, figsize=(11.4, 7.4), sharex=True,
                             gridspec_kw={"height_ratios": [3, 1.3]}, layout="constrained")
    fig.suptitle("USDe traded at different prices across two Binance quote markets", fontsize=15, fontweight="bold")
    axes[0].fill_between(times, values("low"), values("high"), color=BLUE, alpha=0.13,
                         label="USDE/USDT executed low–high")
    axes[0].plot(times, values("vwap"), color=BLUE, lw=2, label="USDE/USDT minute VWAP")
    axes[0].plot(times, quote_values("usdc_pair_approx_vwap_in_usdt"), color=ORANGE, lw=1.6,
                 label="USDE/USDC VWAP × USDC/USDT VWAP")
    axes[0].set_ylabel("USDT per USDe")
    axes[0].set_ylim(0.58, 1.12)
    axes[0].legend(loc="lower right", fontsize=9.5, framealpha=0.97)
    axes[0].set_title("Executed prices; minute conversion is approximate and does not represent executable quotes", loc="left", fontsize=10.5)
    control = {date(r["minute_utc"]): r for r in read("control_minutes.csv") if r["symbol"] == "USDCUSDT"}
    axes[1].plot(times, [float(control[t]["vwap"]) for t in times], color=GREEN, lw=1.7)
    axes[1].set_ylabel("USDT per USDC")
    axes[1].set_title("The quote asset also moved: normalize it before comparing the two USDe pairs", loc="left", fontsize=10.5)
    axes[1].set_xlabel("10 October 2025 · UTC (gray band: Binance's announced 21:36–22:16 window)")
    for ax in axes:
        time_axis(ax)
        shade_official(ax)
    fig.savefig(ROOT / "quote-market-prices.png", dpi=160)
    plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(11.4, 7.2), sharex=True, layout="constrained")
    fig.suptitle("A rising price coexisted with predominantly aggressive selling", fontsize=15, fontweight="bold")
    axes[0].plot(times, values("vwap"), color=BLUE, lw=2)
    axes[0].set_ylabel("USDE/USDT minute VWAP")
    axes[0].set_ylim(0.60, 1.04)
    axes[0].set_title("Exploratory 21:44–21:54 interval: first-to-last minute VWAP rose 36.31%", loc="left", fontsize=10.5)
    axes[1].bar(times, [v * 100 for v in values("taker_sell_quote_share")], width=0.7 / 1440,
                 color=ORANGE, alpha=0.88)
    axes[1].axhline(50, color="#515b66", ls="--", lw=1)
    axes[1].set_ylim(0, 104)
    axes[1].set_ylabel("Taker-sell share of notional (%)")
    axes[1].set_title("81.18% of the interval's USDT notional was seller-initiated; this is not ownership information",
                       loc="left", fontsize=10.5)
    axes[1].set_xlabel("10 October 2025 · UTC (orange band: exploratory recovery interval)")
    for ax in axes:
        time_axis(ax)
        ax.axvspan(date("2025-10-10T21:44:00Z"), date("2025-10-10T21:54:00Z"), color=ORANGE, alpha=0.13)
    fig.savefig(ROOT / "price-and-aggressor-flow.png", dpi=160)
    plt.close(fig)

    rows = read("matched_clock_windows.csv")
    dates = sorted({r["date"] for r in rows})
    fig, ax = plt.subplots(figsize=(11.4, 5.5), layout="constrained")
    x = np.arange(len(dates))
    for symbol, offset, color in [("USDEUSDT", -0.2, BLUE), ("USDEUSDC", 0.2, ORANGE)]:
        lookup = {r["date"]: float(r["base_volume"]) for r in rows if r["symbol"] == symbol}
        ax.bar(x + offset, [lookup[d] for d in dates], width=0.38, color=color,
               label="USDE/" + symbol[4:])
    event_index = dates.index("2025-10-10")
    ax.axvspan(event_index - 0.5, event_index + 0.5, color="#626c76", alpha=0.10)
    ax.set_yscale("log")
    ax.set_xticks(x, [d[5:] for d in dates])
    ax.set_xlabel("Date in 2025 · identical 21:00–23:00 UTC windows")
    ax.set_ylabel("USDe traded (log scale)")
    ax.set_title("The event window had much more turnover than the preceding seven matched windows",
                  fontsize=13, fontweight="bold")
    ax.legend(framealpha=0.98)
    fig.savefig(ROOT / "matched-window-turnover.png", dpi=160)
    plt.close(fig)
    (ROOT / "plot_versions.json").write_text(json.dumps({"matplotlib": matplotlib.__version__,
                                                         "numpy": np.__version__}, indent=2) + "\n")
    print("Wrote three PNG research figures")


if __name__ == "__main__":
    main()
