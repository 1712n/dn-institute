import threading
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd

from src.pm_client import PolymarketClient
from src import osint

_tl = threading.local()


def _client():
    if not hasattr(_tl, "c"):
        _tl.c = PolymarketClient()
    return _tl.c


def fetch_lifetime_parallel(wallets, workers=16):
    def work(w):
        lt = osint._lifetime(_client(), w)
        return w, lt["lt_markets"], lt["lt_pnl"]
    rows = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for fut in as_completed([ex.submit(work, w) for w in wallets]):
            w, m, p = fut.result()
            rows.append({"wallet": w, "lt_markets": m, "lt_pnl": p})
    return pd.DataFrame(rows)


def lifetime_multiplier(lt_markets, lt_pnl):
    if lt_markets is None or lt_markets != lt_markets:
        return 1.0, "no_data"
    lt_markets = int(lt_markets)
    if lt_markets == 0:
        return 1.0, "no_positions"
    M, tag = 1.0, "normal"
    if lt_markets <= 10:
        M += 0.30; tag = "fresh"
    elif lt_markets <= 30:
        M += 0.15; tag = "low_footprint"
    elif lt_markets >= 300:
        M -= 0.35; tag = "very_high_activity"
    elif lt_markets >= 120:
        M -= 0.20; tag = "high_activity"
    if lt_markets >= 80 and lt_pnl <= -20000:
        M -= 0.40; tag = "degen_loser"
    elif lt_markets >= 50 and lt_pnl <= -5000:
        M -= 0.15; tag = "net_loser"
    if lt_markets <= 60 and lt_pnl > 0:
        M += 0.10
        if tag == "normal":
            tag = "clean_profitable"
    return max(0.3, min(1.4, M)), tag


def cooccurrence(ep, window_sec=900, min_shared=2, burst_sec=180, burst_n=3):
    pair_markets = defaultdict(set)
    adj = defaultdict(set)
    edges = []
    for slug, g in ep.groupby("slug"):
        arr = g[["wallet", "entry_ts"]].sort_values("entry_ts").to_numpy()
        n = len(arr)
        for i in range(n):
            burst = {arr[i][0]}
            for j in range(i + 1, n):
                dt = arr[j][1] - arr[i][1]
                if dt > window_sec:
                    break
                if arr[i][0] == arr[j][0]:
                    continue
                pair = tuple(sorted((arr[i][0], arr[j][0])))
                pair_markets[pair].add(slug)
                if dt <= burst_sec:
                    burst.add(arr[j][0])
            # intra-market synchronized burst: many distinct wallets within burst_sec
            if len(burst) >= burst_n:
                bl = sorted(burst)
                for a in bl:
                    for b in bl:
                        if a < b:
                            adj[a].add(b); adj[b].add(a)
                            edges.append((a, b, "burst:" + slug[:24]))
    for (a, b), mk in pair_markets.items():
        if len(mk) >= min_shared:
            adj[a].add(b); adj[b].add(a)
            edges.append((a, b, "xmarket:%d" % len(mk)))
    seen, clusters = set(), []
    for node in adj:
        if node in seen:
            continue
        comp, stack = set(), [node]
        while stack:
            x = stack.pop()
            if x in comp:
                continue
            comp.add(x); seen.add(x)
            stack.extend(adj[x] - comp)
        if len(comp) >= 2:
            clusters.append(comp)
    cid = {}
    for i, comp in enumerate(clusters):
        for w in comp:
            cid[w] = i
    return cid, clusters, edges
