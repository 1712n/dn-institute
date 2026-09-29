# Trade feed validator

The current pipeline trusts the indexer: `parse(event)` goes straight into `insert_into(analytics_table, row)`. This tool puts a validation step in between. It reads the raw feed in arrival order, as a stream consumer would, and routes each row to one of three places:

- **`out/clean_trades.csv`**: rows that passed, in chain order, with normalised values (UTC timestamps, exact decimal amounts) and any warning flags in a `flags` column.
- **`out/dead_letter.jsonl`**: rows that cannot be trusted yet. Each line keeps the raw fields exactly as received plus machine-readable reason codes, so the row can be repaired and pushed through the same pipeline again.
- **dropped**: redeliveries of a trade that was already accepted. They are not copied anywhere, but `out/report.json` names the event each one repeats.

`out/report.json` also has the per-row verdicts, volume totals before and after validation, and suspected round trips. The invariant is simple: rows read = accepted + dropped + dead-lettered.

## Quick start

Python 3.9+. The pipeline uses only the standard library; `pytest` is needed for the tests.

```bash
cd tools/trade_feed_validator
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python pipeline.py sample_feed.csv --feed-date 2026-09-28 --out-dir out
python -m pytest -v
```

The sample timestamps have no date, so `--feed-date` anchors them to one UTC day (any date works for the sample).

Output on the sample:

```
row  event_id  outcome     issues
  1  evt_001   accepted    -
  2  evt_002   accepted    -
  3  evt_003   duplicate   high_ingest_lag; duplicate_trade
  4  evt_004   accepted    -
  5  evt_005   dead_letter missing_required_field
  6  evt_006   accepted    round_trip_suspect
  7  evt_007   duplicate   duplicate_trade
  8  evt_008   dead_letter ingested_before_block_time; ingest_clock_regression; round_trip_suspect

volume: naive 705000 -> clean 375000 (dead_letter 120000, duplicate 210000)
round trip: 0xF6… BUY evt_006 -> SELL evt_008, amount 90000
warning: time-only timestamps anchored to 2026-09-28; a trade near midnight UTC cannot be placed on the right day, the indexer should emit full ISO 8601 timestamps

outputs written to out/
```

Other options:

- `--backfill FILE`: repair null `block_time` from a `tx_hash,block_time` table
- `--max-dead-letter-rate 0.1`: quality gate; above it the run exits 3 and `clean_trades.csv` is not published
- `--strict-identifiers`: require full EVM ids (20-byte wallet, 32-byte tx hash); off by default because the sample ids are shortened
- `--clock-skew-seconds`, `--max-ingest-lag-seconds`, `--round-trip-window-minutes`: thresholds

Exit codes: 0 success, 1 the run could not start or read its input (missing or repeated columns, reserved column names, bad encoding, unbalanced quotes, NUL bytes, a bad backfill file, an output path that would overwrite an input), 2 invalid command-line options, 3 quality gate failed. Outputs from a previous run are removed first, so a failed run never leaves stale files that look current.

## Issues found in the sample

Rows are numbered as in the challenge table.

### 1. Same trade redelivered under a new `event_id` (rows 2, 3)

`evt_003` repeats `evt_002`: same `tx_hash` 0xaa2, wallet, side, amount and block time, ingested 2m38s later. The likely cause is an indexer retry after a timeout. Because the indexer assigns a fresh `event_id` per delivery, deduplicating on `event_id` does not catch it.

**Downstream:** 0xD4 buy volume becomes 360,000 instead of 240,000, its trade count 3 instead of 2, and that print gets double weight in VWAP. Wallet activity and "most active wallet" rankings inflate.

**Handling:** dropped as `duplicate_trade`, linked to `evt_002` in the report. Dedup keys on the on-chain identity, not on `event_id` (see [Dedup key](#dedup-key)).

### 2. Double emission (rows 6, 7)

`evt_007` is identical to `evt_006` in every field except `event_id`, including the ingest second. This looks like the producer emitting one log twice, for example a batch flushed twice.

**Downstream:** +90,000 volume. Worse, it hides behaviour: with the duplicate, 0xF6 looks like it bought 180,000 and sold 90,000 (net accumulation). Deduplicated, it bought 90,000 and sold 90,000 (flat), which is what makes issue 5 visible.

**Handling:** dropped as `duplicate_trade`, linked to `evt_006`.

### 3. Missing `block_time` (row 5)

`evt_005` has `block_time = null`.

**Downstream:** the trade cannot be placed in any time bucket. Hourly volume and VWAP windows either lose it silently (a `WHERE block_time BETWEEN` filter drops NULLs, so 0xE5 sell volume reads 45,000 instead of 75,000) or put it first or last in any time sort.

**Handling:** dead-lettered. See [How `evt_005` is handled](#how-evt_005-is-handled).

### 4. Ingested before its block existed (row 8)

`evt_008` has `ingested_at` 09:59:50, 10m10s before its `block_time` 10:10:00. That is impossible, so one of the two clocks is wrong.

The feed says which one. `block_time` 10:10:00 fits chain order after rows 6 and 7 (10:03:11). `ingested_at` runs backwards: row 8 arrived after rows 6 and 7 but claims to be ingested 3m25s before them. The validator records this as a separate `ingest_clock_regression` flag, which points at our ingest clock (a skewed worker, or `ingested_at` filled from the wrong field) rather than at the chain.

**Downstream:** freshness and latency metrics go negative. Anything that uses processing time for watermarks or late-data cutoffs misplaces the row. If `block_time` were the wrong field instead, the trade would sit in the wrong VWAP window.

**Handling:** dead-lettered as `ingested_before_block_time` (5s clock-skew tolerance). The evidence points at the ingest clock, but it is inference from three rows, not proof, and the two mistakes are not equally costly: a wrong `block_time` in the clean table silently moves 90,000 of volume into another window, while a row held back for one lookup costs minutes. The repair is the same as for `evt_005`: confirm `block_time` from the chain by `tx_hash`, re-stamp `ingested_at`, replay.

### 5. Round trip by one wallet, possible wash trade (rows 6, 8)

0xF6 buys 90,000 (`evt_006`, 10:03:11) and sells 90,000 (`evt_008`, 10:10:00), 6m49s apart, with no net position change.

**Downstream:** this is valid data but a market-health signal. It adds 180,000 of volume that carries no economic exposure, which is exactly what volume and wash-trading metrics must separate out. It also links the two trades for wallet clustering.

**Handling:** both legs get a `round_trip_suspect` flag (same wallet, opposite sides, equal amount, within 30 minutes). They are not removed: the trades happened on chain, so the flag lets each metric decide. Detection runs on unique trades including dead-lettered ones that still have a `block_time`; otherwise quarantining `evt_008` would hide the pattern. Each trade is counted once by its trade key and each leg is paired at most once (legs are matched in time order), so redeliveries cannot inflate the flagged volume.

### 6. Arrival order is not chain order (whole feed)

The feed is delivered in arrival order and the brief says it is not guaranteed to match chain order. In the sample, `ingested_at` order already disagrees with arrival order (row 8), and row 5 has no position at all. The naive pipeline inserts in arrival order.

**Downstream:** running VWAP, first and last price per window, cumulative volume and any "next trade by this wallet" logic used for clustering assume insertion order is time order.

**Handling:** accepted rows are written sorted by `block_time`. A row older than the latest accepted `block_time` (the watermark) gets a `late_arrival` flag, so a streaming consumer knows it must revise a closed window.

### 7. Contract gaps (whole feed)

- **Time-only timestamps.** No date and no zone marker, so a trade at 23:59:59 ingested at 00:00:02 looks like issue 4. The pipeline anchors them with `--feed-date`, warns, and accepts full ISO 8601 with offsets (normalised to UTC).
- **No `log_index`.** One transaction can emit several fills, so `tx_hash` alone is not a trade identity. When a `log_index` column is present it is used; see [Dedup key](#dedup-key).
- **No price or quote amount.** A volume-weighted price needs a price per trade, and this schema does not carry one; `amount` has no token or unit either. That is a fix for the indexer schema, not for a validator.

## Dedup key

`event_id` is assigned per delivery, so it is not an idempotency key. Two checks run:

1. Same `event_id`, same payload: exact redelivery, dropped (`duplicate_event`). Same `event_id`, different payload: `event_id_collision`, dead-lettered.
2. Same on-chain trade: `(tx_hash, log_index)` when the feed has `log_index`, otherwise `(tx_hash, wallet, side, amount)`. Same key and same payload: dropped. Same key but a different `block_time` (or, with `log_index`, a different wallet, side or amount): the newcomer is dead-lettered as `conflicting_duplicate` and the already accepted original gets a `disputed_trade` flag, because the conflict signals a reorg or a bad re-read and must not be settled silently on either side. This also applies when the conflicting copy reuses the original `event_id`.

Without `log_index`, two genuinely identical fills in one transaction would collapse into one. On this feed that is the safer error: duplicate deliveries are common (2 of 8 rows), identical fills inside one transaction are rare, and a wrong collapse is visible in the report while a double count is not. Hex identifiers are compared case-insensitively (`0xAB` equals `0xab`); non-hex ones (for example base58) stay case-sensitive. Accepted events are remembered, and a dropped duplicate reserves its `event_id`; a dead-lettered row is not remembered, so it never blocks its own corrected redelivery. The state here lives in memory for one batch; in a long-running stream it belongs in the sink as a unique constraint on the trade key, or in a store with a retention horizon longer than the indexer's redelivery window.

## How `evt_005` is handled

**Dead-letter queue, with automatic backfill from the chain when a lookup is available.**

- **Not dropped:** the transaction exists, so dropping it silently removes 30,000 of 0xE5 sell volume (40% of that wallet's sells), and nothing would ever fetch it again.
- **Not backfilled by guessing:** `block_time` is not an estimate; it is a fact on chain, retrievable by `tx_hash` (transaction receipt, then block timestamp). Guessing from `ingested_at` (09:58:30) assumes a known lag, and row 8 shows our ingest clock cannot be trusted. Interpolating between neighbours assumes an ordering the feed does not guarantee.
- **So:** the row goes to `dead_letter.jsonl` with its raw fields and reason. A repair job resolves `block_time` by `tx_hash` and replays the row through the same pipeline. `parse_event` takes a `resolve_block_time` callable for this; `--backfill` feeds it from a file as a stand-in for a node RPC. With it, `evt_005` is accepted with a `block_time_backfilled` flag (see `test_backfill_from_chain_repairs_evt_005`).

**What would change the answer:**

- A cheap, synchronous node lookup inside the pipeline: backfill inline, with the flag, and skip the queue.
- The transaction is not found on chain (dropped, reorged out, fabricated): drop it permanently, with an audit record.
- Many rows with null `block_time`: that is an indexer bug, not bad luck. Stop the batch (`--max-dead-letter-rate`) and fix the source instead of repairing rows one by one.
- A consumer that needs only daily totals, with the day known from the partition, could count the row without an exact time.

## General practice (150 words or fewer)

Treat the feed as a contract and test it at the boundary, not in dashboards. A rules gate like this one runs before any insert, and failing rows go to a dead-letter table with a reason; nothing enters or disappears silently. Make writes idempotent on the on-chain identity (chain, tx_hash, log_index) with a unique constraint, so a retry cannot double count whatever `event_id` the indexer assigns. Publish per-batch quality metrics (dead-letter rate, duplicate rate, ingest lag, clock regressions) and fail the batch or page someone when they cross a threshold. Finally, reconcile daily against an independent source, such as a second indexer or direct node reads, comparing trade counts and volume per block range. Rules catch the problems we already know about; reconciliation catches the ones nobody has thought of yet.

## Beyond the sample

Checks that the sample does not trigger but a real feed will (covered in `tests/test_rules.py` and `tests/test_pipeline.py`):

- null tokens (`""`, `null`, `None`, `NaN`, `n/a`), invalid sides, non-positive amounts, `NaN`/`Infinity`, `1_000`, non-ASCII digits
- amounts as exact `Decimal` with enough precision for wei-scale values (uint256 range, up to 36 decimals), written in canonical form (`1.2E+5` and `120000.00` both become `120000`)
- timestamps parsed by an explicit pattern rather than `datetime.fromisoformat`, whose accepted formats changed between Python versions (tests run on 3.9 and 3.12): ISO 8601 with offsets normalised to UTC, nanoseconds truncated, date-only values and years outside 1970 to 2999 rejected, time-only and full timestamps mixed in one row or one feed
- rows with more values than the header (extra values kept for repair) or fewer; extra named columns pass through to the clean output
- `event_id` reused for a different trade, including the `event_id` of a dropped duplicate; the same trade reported with a different block time or payload (reorg signal) flagged on both sides
- several distinct fills in one transaction are kept; `log_index` support
- late arrivals against a watermark; ingest clock going backwards, advanced only by rows that were not rejected
- an unbalanced quote fails the feed instead of silently swallowing every following line into one field; so do missing, repeated or reserved columns, invalid UTF-8 and NUL bytes (exit code 1); a byte-order mark is tolerated; an empty feed raises a warning
- invalid UTC offsets (`+24:00`), shortened ids keep their case (`0xD4…` is not hex), optional strict EVM id format check
- a failed quality gate withholds `clean_trades.csv`; a backfill table with two block times for one transaction is refused
- the input and the backfill file can never be overwritten by an output, including on case-insensitive file systems
- all outputs are built in memory before anything is written, and each file is written to a unique temp name and renamed

## Layout

```
records.py    parsing: raw CSV row -> TradeEvent + issues, never raises on bad values
rules.py      record rules, dedup, ordering checks, round-trip detection
pipeline.py   orchestration, outputs, CLI
tests/        one test per sample issue (test_sample_feed.py), edge cases, CLI
```

To add a check, write `def my_rule(ev: TradeEvent, cfg: Config) -> None` that calls `ev.add(code, REJECT or FLAG, detail)` and append it to `RECORD_RULES` in `rules.py`.
