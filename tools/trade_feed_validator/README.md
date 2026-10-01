# Trade feed validator

A small, dependency-free validator that sits between a trade event feed (blockchain indexer, exchange API) and the analytics table. It replaces the current pipeline

```
for event in feed_stream:
    row = parse(event)
    insert_into(analytics_table, row)
```

with `parse -> validate -> route`. Every event gets exactly one decision:

| Status | Meaning | Where it goes |
|---|---|---|
| `ACCEPTED` | safe for analytics, possibly with warnings | `clean.csv`, sorted by `block_time` |
| `DUPLICATE` | this trade was already accepted | `duplicates.csv`, with `duplicate_of` |
| `DEAD_LETTER` | broken, must not reach analytics | `dead_letter.csv`, with reasons, replayable |

## Quick start

Requires Python 3 (tested with 3.11). Only the standard library is used, so there is nothing to install.

```bash
cd tools/trade_feed_validator

# run the tests
python3 -m unittest -v

# run the pipeline on the sample feed
python3 pipeline.py sample_feed.csv --out-dir output

# optional: same tests with pytest
python3 -m pip install pytest
python3 -m pytest -v
```

Pipeline options:

- `--feed-date YYYY-MM-DD`: the date for time-only timestamps such as `09:14:02`. The sample feed only states that all events happened on the same day, so the default is a fixed placeholder date. Only the order of events matters here.
- `--fail-on-dead-letter`: exit with code 1 if any event was rejected. Use it in CI or for alerting.

Output for the sample feed:

```
evt_001    ACCEPTED
evt_002    ACCEPTED
evt_003    DUPLICATE    duplicate_of=evt_002
           - [DUPLICATE] DUPLICATE_TRADE: same trade already accepted as evt_002
evt_004    ACCEPTED
evt_005    DEAD_LETTER
           - [ERROR] MISSING_FIELD: 'block_time' is missing
evt_006    ACCEPTED
evt_007    DUPLICATE    duplicate_of=evt_006
           - [DUPLICATE] DUPLICATE_TRADE: same trade already accepted as evt_006
evt_008    DEAD_LETTER
           - [WARNING] INGEST_CLOCK_WENT_BACKWARDS: ingested_at is 205s earlier than an event that arrived before it
           - [ERROR] INGESTED_BEFORE_BLOCK_TIME: ingested_at is 610s before block_time (tolerance 5s)

input=8 accepted=4 duplicates=2 dead_letter=2
volume: naive=705000 validated=375000
```

The naive pipeline reports **705,000** of volume. The validated volume is **375,000**, so the naive figure is **88% too high**.

## Data-quality issues in the sample

### 1. Redelivered event under a new `event_id`: `evt_003` (duplicate of `evt_002`)

`evt_003` has the same `tx_hash`, wallet, side, amount and `block_time` as `evt_002`. Only its `event_id` is new, and it was ingested 2m38s later. This is the typical pattern of an indexer retry after a timeout.

**Downstream impact:**
- Volume is inflated by 120,000.
- Trade counts and wallet activity are inflated, so `0xD4…` looks like it made 3 buys instead of 2.
- The trade gets double weight in VWAP.
- In wallet clustering, a wallet that repeats identical trades looks bot-like, so the duplicate creates false behavioural signals.

`event_id` cannot serve as the idempotency key, because it identifies the *delivery*, not the *trade*.

### 2. Double-emitted event: `evt_007` (duplicate of `evt_006`)

This row matches `evt_006` in every field except `event_id`, including the same `ingested_at`. The producer emitted the event twice, for example from two partitions or two consumers on the same topic. The impact is the same as in issue 1 (+90,000 volume). It is a separate failure mode because it cannot be explained by a retry, so the cause has to be fixed in a different part of the upstream system.

**Handling (issues 1 and 2):** events are deduplicated on the *trade* key `(tx_hash, wallet, side, amount, block_time)`. The first accepted copy is kept, and later copies go to `duplicates.csv` with a `duplicate_of` link, so the drop can be audited. `tx_hash` alone is deliberately **not** used as the key: one transaction can contain several trades (multi-hop swaps, batch fills), and collapsing them would undercount. This case has a test (`test_multiple_trades_in_one_tx_are_kept`). `evt_001` and `evt_002` (same wallet, side and amount, different tx) are also correctly kept as two trades. The right key in production would be `(chain_id, tx_hash, log_index)`, but the feed does not have `log_index` (see issue 7).

### 3. Missing `block_time`: `evt_005`

**Downstream impact:**
- The trade cannot be placed in any time bucket. Hourly volume and VWAP either silently skip it, because `WHERE block_time BETWEEN …` drops nulls, or a total-volume query counts it. Two dashboards built from the same table would then disagree.
- Anything ordered by time (first/last trade, holding periods, sequences per wallet) either sorts the null first or last, or fails.
- Here it is a SELL by `0xE5…`, which also sold 6 minutes earlier, so the wallet's sequence becomes ambiguous.

See [How `evt_005` is handled](#how-evt_005-is-handled) below.

### 4. Ingested before it happened: `evt_008`

`ingested_at` (09:59:50) is 10m10s **earlier** than `block_time` (10:10:00), which is physically impossible. Either the indexer reported a wrong block or block time, or the ingester's clock is wrong. Issue 5 makes the clock the likely suspect, but from the feed alone we cannot know which value to trust.

**Downstream impact:**
- Ingestion-lag and freshness metrics get negative values, which skew averages and hide real delays.
- If `block_time` is wrong, the event lands in the wrong time bucket.
- It also creates a **fake behavioural pattern**. With these timestamps, `0xF6…` buys 90,000 at 10:03:11 and sells exactly 90,000 at 10:10:00, which is a 7-minute round trip that wash-trading or flipping heuristics would flag. If the true block time is at or before 09:59:50, the SELL happened *before* the BUY, and the pattern reads the opposite way.

**Handling:** dead-lettered as `INGESTED_BEFORE_BLOCK_TIME`. A 5-second tolerance (`clock_skew_tolerance`) allows for ordinary clock skew between the node and the ingester.

### 5. Ingestion clock goes backwards: `evt_008`

`evt_008` arrived after `evt_007` (ingested 10:03:15) but carries `ingested_at` 09:59:50, which is 3m25s earlier. Arrival order and ingestion time disagree, so the ingester's clock (or one of several ingester hosts) is wrong.

**Downstream impact:** any incremental job that uses `ingested_at` as a watermark (`WHERE ingested_at > :last_checkpoint`) would **skip `evt_008` permanently**, because its timestamp is older than the checkpoint already processed. Volume would be lost without any error. Latency metrics would also be wrong.

**Handling:** `INGEST_CLOCK_WENT_BACKWARDS` warning, with a 60-second tolerance for normal jitter between parallel workers. It is a warning rather than an error because it says something about the *ingester*, not about the trade. In this sample the event is rejected anyway by issue 4.

### 6. Arrival order is not chain order (whole feed)

The feed is documented as arrival order, not chain order, but the current pipeline inserts rows as they arrive. Anything that assumes insertion order equals time order then breaks: running balances, cumulative volume, "last price", and per-wallet sequences such as BUY-then-SELL.

**Handling:**
- `clean.csv` is sorted by `block_time`.
- Every accepted event that is older than an already accepted event gets an `OUT_OF_ORDER` warning, so windowed aggregates that include it can be recomputed. `allowed_lateness` sets how late an event may be before it is flagged.

In this sample, once duplicates and dead letters are removed, the accepted events happen to be in chain order. The check exists for real feeds.

### 7. Schema gaps (not tied to a single row)

These cannot be fixed in the validator, but they limit what can be validated and should go back to the feed owner:

- **No price field.** VWAP, one of the stated target metrics, cannot be computed from this feed at all.
- **`amount` has no unit.** It could be token units, raw integer units before applying decimals, or quote currency. Mixing these up corrupts volume by orders of magnitude.
- **No `log_index`, `block_number` or `chain_id`.** Without them there is no exact idempotency key. Chain reorganisations cannot be detected (the same tx can appear in a different block after a reorg), and one tx in two blocks can only be caught heuristically (see `TX_BLOCK_TIME_CONFLICT` below).
- **Timestamps without a date or timezone.** Time-only values break at midnight. The validator also accepts ISO 8601 and Unix epoch values.

## How `evt_005` is handled

**Decision: dead-letter queue.**

- **Not drop.** The row is otherwise a valid trade with a real `tx_hash` and 30,000 of volume. Dropping it would undercount volume and leave no trace that anything was lost.
- **Not backfill from `ingested_at`.** In this very sample, ingest lag ranges from 3 seconds to 2m38s, and issue 5 shows the ingest clock itself cannot be trusted. Backfilling could place the trade in the wrong minute or hour bucket and in the wrong order relative to the same wallet's previous SELL (`evt_004`).
- **Dead-letter.** The event stays out of the metrics but remains visible, with its reason, and can be replayed. The validator only remembers *accepted* events, so after a fix the same `event_id` can be replayed and will be accepted (`test_dead_lettered_event_can_be_replayed_after_fix`). The right fix is an authoritative backfill: look up `0xaa4` on chain (`eth_getTransactionReceipt` → `blockNumber` → `eth_getBlockByNumber` → `timestamp`).

**What would change the answer:**
- **The pipeline has RPC access to a node or archive.** Backfill inline from the chain. The value is authoritative, so it does not need to wait in a queue.
- **Consumers only need daily totals, and the event is clearly within the day.** Backfill with `ingested_at`, add an `is_estimated` flag, and accept the event.
- **Missing values are systematic** (a large share of the feed, or a new indexer version). Fix it upstream and alert instead of filling the queue. A DLQ only works when it receives the exceptions.
- **The tx does not exist on chain** (phantom event). Drop it and log why.

## Additional checks (beyond the sample)

All of these have tests in `test_validator.py`.

| Check | Status | Why |
|---|---|---|
| Missing required field; any of `null`, `""`, `None`, `NaN`, `n/a` | DEAD_LETTER | different producers spell null differently |
| `side` not BUY/SELL (case-insensitive) | DEAD_LETTER | unknown sides silently disappear from buy/sell splits |
| `amount` ≤ 0, non-numeric, `Infinity` | DEAD_LETTER | one bad value breaks every sum it is part of |
| Unparseable timestamp | DEAD_LETTER | |
| Same `event_id`, same payload | DUPLICATE | plain redelivery |
| Same `event_id`, **different** payload | DEAD_LETTER (`EVENT_ID_CONFLICT`) | IDs are being reused, so we can't tell which payload is right |
| Same `tx_hash` with a **different** `block_time` | DEAD_LETTER (`TX_BLOCK_TIME_CONFLICT`) | a tx is mined in one block; points to a reorg or an indexer bug |
| EVM ids differ only in letter case (`0xAbC` vs `0xabc`) | normalised before dedup | EIP-55 checksum casing would split one wallet in two for clustering; non-`0x` ids (e.g. Solana base58) keep their case |
| Ingest lag > 5 min | WARNING (`LATE_ARRIVAL`) | the time windows it falls into have already been reported |
| Same wallet, opposite side, same amount within 1 h | WARNING (`ROUND_TRIP`) | possible wash trade or flip, worth a look by analysts |

Amounts are parsed as `Decimal`, not `float`, so sums are exact. All thresholds are arguments of `TradeFeedValidator`.

## Preventing this class of problems (general practice)

Put a validation gate with a written data contract at ingestion. It enforces schema, types, nulls and invariants (`block_time ≤ ingested_at`, one block per tx, unique `(chain_id, tx_hash, log_index)`) and routes failures to a dead-letter queue instead of to analytics. Make writes idempotent: upsert on the natural trade key, never on the delivery ID. Monitor the gate itself: alert on dead-letter rate, duplicate rate and ingest lag, because a sudden change is usually an upstream release. Reconcile daily: compare trade counts and volume per pool against an independent source, either chain RPC or a second indexer, and alert when they diverge. Version the contract and run the validator in CI on recorded feed samples, so a feed change fails a build before it can corrupt a dashboard.

## Files

| File | Purpose |
|---|---|
| `validator.py` | `TradeFeedValidator`: streaming checks, one `Decision` per event |
| `pipeline.py` | CLI: CSV in → `clean.csv`, `duplicates.csv`, `dead_letter.csv`, `report.json` |
| `test_validator.py` | 34 tests: each sample issue, edge cases, end-to-end run |
| `sample_feed.csv` | the sample feed from the challenge |

Known limitations:
- State (seen trades) is kept in memory and grows with the stream. In production it belongs in a keyed store with a TTL longer than the indexer's maximum redelivery delay.
- Time-only timestamps cannot cross midnight.
- Without `log_index`, two genuinely identical trades in one transaction (same wallet, side and amount) would be merged.
