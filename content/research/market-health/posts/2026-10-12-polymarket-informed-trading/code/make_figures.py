"""Regenerate every figure in the write-up from the trade tape and the pipeline outputs."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import duckdb
import pandas as pd

import config
from src import controls

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "svg.hashsalt": "pm"})
PRICE = "#708090"
BUY = "#c0392b"
LINE = "#2c3e50"
SHADE = "#f5d78e"
TIER_COLORS = {"HIGH": "#c0392b", "MED-HIGH": "#e67e22", "MED": "#f1c40f",
               "LOW-MED": "#7fb3d5", "LOW": "#bdc3c7"}

MADURO = "maduro-out-by-january-31-2026-318"
MADURO_WALLET = "0x31a56e9e690c621ed21de08cb559e9524cdb8ed9"
CARACAS_FIRST_BLASTS = pd.Timestamp("2026-01-03 05:50")   # first explosions reported (~1:50am VET)
CALL_SLUGS = ["will-trump-talk-to-nicols-maduro-by-december-31",
              "will-trump-talk-to-nicols-maduro-in-november-489-645"]
CALL_WALLET = "0xaec0bf01dbdb9e874ba26afad77c42386c885a19"
CALL_WINDOW = (pd.Timestamp("2025-11-20"), pd.Timestamp("2025-11-24"))  # private call, per NYT
IRAN = "will-the-us-next-strike-iran-on-february-28-2026-et"
IRAN_WALLET = "0x8517b980e32611ed689e64c131e841a094002ce5"
TOWN_SLUGS = ["will-russia-capture-kostyantynivka-by-march-31-872-578",
              "will-russia-capture-lyman-by-march-31-2026-494"]
TOWN_WALLET = "0x54520a0661afd0c6580ce45773097c0f0c2f6f80"

FIGURES = ["maduro-timeline.png", "event-relevance.png", "iran-baserate.png",
           "russia-towns-timeline.png", "maduro-call-0xaec0bf.png", "iran-strike-0x8517.png"]


def winner_path(con, slug):
    df = con.execute("""
        SELECT t.timestamp ts, t.size, t.wallet, t.side, t.outcome_index = m.win_index on_winner,
               CASE WHEN t.outcome_index = m.win_index THEN t.price ELSE 1 - t.price END wp,
               t.size * t.price notional
        FROM trades t JOIN markets m USING (condition_id)
        WHERE m.slug = ?
        ORDER BY t.timestamp, t.tx_hash, t.wallet, t.price, t.size""", [slug]).df()
    df["t"] = pd.to_datetime(df["ts"], unit="s")
    return df


def wallet_buys(path, wallet):
    return path[(path["wallet"] == wallet) & (path["side"] == "BUY") & path["on_winner"]]


def jump_of(slug):
    for name in ["surprise_substantive.csv", "wallet_seed_markets.csv"]:
        df = pd.read_csv(config.OUTPUT_DIR / name)
        hit = df[df["slug"] == slug]
        if len(hit):
            return pd.to_datetime(int(hit.iloc[0]["jump_ts"]), unit="s")
    raise KeyError(slug)


def price_panel(ax, path, buys, start=None, end=None, scale=1.0):
    p = path if start is None else path[(path["t"] >= start) & (path["t"] <= end)]
    ax.plot(p["t"], p["wp"], color=PRICE, lw=0.9, drawstyle="steps-post")
    ax.scatter(buys["t"], buys["price"] if "price" in buys else buys["wp"],
               s=(buys["notional"] * scale).clip(20, 600), color=BUY, edgecolor="white",
               linewidth=0.8, zorder=3)
    ax.set_ylim(0, 1.02)


def save(fig, name):
    config.FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(config.FIGURES_DIR / name, dpi=110, bbox_inches="tight", metadata={"Software": None})
    plt.close(fig)


def fig_maduro(con):
    path = winner_path(con, MADURO)
    buys = wallet_buys(path, MADURO_WALLET).assign(price=lambda d: d["wp"])
    jump = jump_of(MADURO)
    fig, ax = plt.subplots(figsize=(9.5, 4.6))
    price_panel(ax, path, buys, path["t"].min(), jump + pd.Timedelta(hours=3), scale=0.03)
    ax.axvline(CARACAS_FIRST_BLASTS, color=LINE, ls=":", lw=1)
    ax.axvline(jump, color=LINE, ls="--", lw=1)
    ax.text(jump + pd.Timedelta(hours=4), 0.62,
            f"first blasts in Caracas ~{CARACAS_FIRST_BLASTS:%H:%M} UTC (dotted)\n"
            f"capture announced {jump:%b %d, %H:%M} UTC (dashed)", fontsize=8.5, va="center")
    ax.plot([], [], color=PRICE, label="Market price: 'Maduro out by Jan 31' (YES)")
    ax.scatter([], [], color=BUY, label="Wallet 0x31a56e… buys (size ∝ $)")
    ax.legend(loc="upper left", fontsize=8.5)
    ax.set_ylabel("Implied probability (YES)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    last = buys["t"].max()
    ax.set_title(f"Accumulation at ~{buys['notional'].sum() / buys['size'].sum() * 100:.0f}¢; "
                 f"last buy {last:%H:%M} UTC, {(jump - last).total_seconds() / 3600:.1f}h before "
                 f"the announcement", fontsize=11)
    save(fig, "maduro-timeline.png")


def fig_event_relevance():
    tiers = pd.read_csv(config.OUTPUT_DIR / "event_tiers.csv")
    counts = tiers["tier"].value_counts().reindex(controls.TIERS, fill_value=0)
    public = int(counts["LOW"] + counts["LOW-MED"])
    fig, ax = plt.subplots(figsize=(8, 3.8))
    bars = ax.bar(counts.index, counts.values, color=[TIER_COLORS[t] for t in counts.index])
    for b, v in zip(bars, counts.values):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.3, str(v), ha="center", fontsize=10)
    ax.set_ylabel("markets")
    ax.set_title(f"{len(tiers)} candidate markets by insider-relevance (OSINT tier)", fontsize=11)
    ax.text(0.98, 0.92, f"{public}/{len(tiers)} explained by public events", transform=ax.transAxes,
            ha="right", color="#555555")
    save(fig, "event-relevance.png")


def fig_iran_baserate():
    ep = pd.read_csv(config.OUTPUT_DIR / "episode_scores.csv")
    top = ep[ep["slug"] == IRAN].sort_values(["S_base", "wallet"], ascending=[False, True]).head(10)
    fan = top[top["series_bets"] >= 3].sort_values(["series_bets", "wallet"])
    labels = [p if isinstance(p, str) else w[:10] + "…" for p, w in zip(fan["pseudonym"], fan["wallet"])]
    fig, ax = plt.subplots(figsize=(8, 0.6 * len(fan) + 1.6))
    ax.barh(labels, fan["series_bets"], color="#95a5a6", label="Strike-dates bet (YES, cheap)")
    ax.barh(labels, fan["series_wins"], color=BUY, label="Dates that actually won")
    ax.set_xlabel("number of date-markets")
    ax.legend(loc="lower right", fontsize=8.5)
    ax.set_title("Survivorship control: top 'Iran-strike' episodes that bet many dates", fontsize=11)
    save(fig, "iran-baserate.png")


def fig_russia_towns(con):
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.4), sharey=True)
    for ax, slug, town in zip(axes, TOWN_SLUGS, ["Kostiantynivka", "Lyman"]):
        path = winner_path(con, slug)
        buys = wallet_buys(path, TOWN_WALLET).assign(price=lambda d: d["wp"])
        price_panel(ax, path, buys, scale=0.15)
        vwap = buys["notional"].sum() / buys["size"].sum()
        ax.set_title(f"'Russia captures {town} by Mar 31' → NO  (entry ~{vwap * 100:.0f}%)", fontsize=10)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    axes[0].set_ylabel("Implied probability (NO)")
    fig.suptitle("Wallet 0x54520a…: cheap bets that the towns would hold (red = buys of NO, size ∝ $)",
                 fontsize=11)
    save(fig, "russia-towns-timeline.png")


def fig_maduro_call(con):
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.4), sharey=True)
    for ax, slug, label in zip(axes, CALL_SLUGS, ["by Dec 31", "November"]):
        path = winner_path(con, slug)
        buys = wallet_buys(path, CALL_WALLET).assign(price=lambda d: d["wp"])
        jump = jump_of(slug)
        start = pd.Timestamp("2025-11-05")
        price_panel(ax, path, buys, start, jump + pd.Timedelta(days=5), scale=0.3)
        ax.axvspan(*CALL_WINDOW, color=SHADE, alpha=0.5, lw=0)
        ax.axvline(jump, color=LINE, ls="--", lw=1)
        vwap = buys["notional"].sum() / buys["size"].sum()
        ax.set_title(f"'Trump talks to Maduro' ({label}) — entry ~{vwap * 100:.0f}%", fontsize=10)
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    axes[0].text(CALL_WINDOW[0] + pd.Timedelta(days=2), 0.93, "private\ncall", ha="center",
                 fontsize=9, color="#7d6608")
    axes[1].text(jump_of(CALL_SLUGS[1]) + pd.Timedelta(hours=8), 0.6, "NYT reports\n(Nov 28)", fontsize=8.5)
    axes[0].set_ylabel("Implied probability (YES)")
    fig.suptitle("Wallet 0xaec0bf01…: bought the Maduro-call outcome in the private-call window, "
                 "before the NYT report", fontsize=11)
    save(fig, "maduro-call-0xaec0bf.png")


def fig_iran_strike(con):
    ep = pd.read_csv(config.OUTPUT_DIR / "episode_scores.csv")
    row = ep[(ep["slug"] == IRAN) & (ep["wallet"] == IRAN_WALLET)].iloc[0]
    path = winner_path(con, IRAN)
    buys = wallet_buys(path, IRAN_WALLET).assign(price=lambda d: d["wp"])
    jump = jump_of(IRAN)
    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    price_panel(ax, path, buys, jump - pd.Timedelta(days=7), jump + pd.Timedelta(days=5), scale=1.0)
    ax.axvline(jump, color=LINE, ls="--", lw=1)
    ax.text(jump + pd.Timedelta(hours=3), 0.55, f"strike public\n({jump:%b %d, %H:%M} UTC)", fontsize=8.5)
    ax.plot([], [], color=PRICE, label="'US strikes Iran on Feb 28' (YES)")
    ax.scatter([], [], color=BUY, label="Wallet 0x8517b9… buys")
    ax.legend(loc="center left", fontsize=8.5)
    ax.set_ylabel("Implied probability (YES)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    vwap = buys["notional"].sum() / buys["size"].sum()
    ax.set_title(f"US strike on Iran: entry at ~{vwap * 100:.0f}¢ — the wallet bet "
                 f"{int(row['series_bets'])} strike-dates, won {int(row['series_wins'])}",
                 fontsize=11, color="#7d6608")
    save(fig, "iran-strike-0x8517.png")


def main():
    con = duckdb.connect(str(config.DB_PATH), read_only=True)
    fig_maduro(con)
    fig_event_relevance()
    fig_iran_baserate()
    fig_russia_towns(con)
    fig_maduro_call(con)
    fig_iran_strike(con)
    con.close()
    print(f"figures written to {config.FIGURES_DIR}: {', '.join(FIGURES)}")


if __name__ == "__main__":
    main()
