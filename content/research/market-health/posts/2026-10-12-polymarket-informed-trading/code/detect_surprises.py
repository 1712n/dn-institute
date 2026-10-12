import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import duckdb
import pandas as pd

import config

MECH = (r"tweets|truth-social-posts|-posts-|will-trump-say|-say-|mention|shake-hands|"
        r"photographed|fact-check|of-truth-social|turnout|number-of")


def main():
    con = duckdb.connect(str(config.DB_PATH), read_only=True)
    sql = """
    WITH m AS (SELECT condition_id, win_index, slug, question, win_outcome, volume, trades_capped, end_date FROM markets),
    t AS (SELECT tr.condition_id cid, tr.timestamp ts, tr.size sz,
            CASE WHEN tr.outcome_index=m.win_index THEN tr.price ELSE 1-tr.price END wp
          FROM trades tr JOIN m ON tr.condition_id=m.condition_id),
    span AS (SELECT cid, min(ts) o, max(ts) c, count(*) n FROM t GROUP BY 1),
    tf AS (SELECT t.cid, t.ts, t.sz, t.wp,
            CASE WHEN span.c>span.o THEN (t.ts-span.o)/CAST(span.c-span.o AS DOUBLE) ELSE 1 END frac
           FROM t JOIN span ON t.cid=span.cid),
    agg AS (SELECT cid,
            sum(CASE WHEN frac<=0.2 THEN sz*wp END)/NULLIF(sum(CASE WHEN frac<=0.2 THEN sz END),0) p_early,
            sum(CASE WHEN frac>=0.9 THEN sz*wp END)/NULLIF(sum(CASE WHEN frac>=0.9 THEN sz END),0) p_late,
            min(CASE WHEN wp>=0.8 THEN ts END) jump_ts
          FROM tf GROUP BY 1)
    SELECT m.slug, m.question, m.win_outcome wout, round(m.volume) vol, m.trades_capped capped, span.n n_tr,
           round(agg.p_early,3) p_early, round(agg.p_late,3) p_late, round(agg.p_late-agg.p_early,3) swing,
           agg.jump_ts, m.end_date
    FROM agg JOIN m ON agg.cid=m.condition_id JOIN span ON agg.cid=span.cid
    WHERE m.volume>=50000 AND span.n>=100 AND agg.p_early<=0.55 AND agg.p_late>=0.80
    ORDER BY (agg.p_late-agg.p_early) DESC, m.volume DESC
    LIMIT 60"""
    df = con.execute(sql).df()
    con.close()
    config.OUTPUT_DIR.mkdir(exist_ok=True)
    df.to_csv(config.OUTPUT_DIR / "surprise_markets.csv", index=False)

    sub = df[~df["slug"].str.contains(MECH, case=False, regex=True)].copy()
    sub.to_csv(config.OUTPUT_DIR / "surprise_substantive.csv", index=False)
    print(f"surprise markets: {len(df)}; substantive: {len(sub)}")


if __name__ == "__main__":
    main()
