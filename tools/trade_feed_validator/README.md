# Trade feed validator

Replaces the original load loop

```
for event in feed_stream:
    row = parse(event)
    insert_into(analytics_table, row)
```

with a validating pipeline. Each row ends up with exactly one outcome, and nothing is lost without a record:

- **accepted**: normalised and written to `clean_trades.csv` in chain order;
- **duplicate**: dropped, recorded in `duplicates.jsonl` with the canonical event it copies;
- **dead letter**: kept out of analytics and written to `dead_letter.jsonl` with reason codes and the untouched raw row, so it can be repaired and replayed.

The pipeline uses only the Python standard library (3.9+, tested on 3.9, 3.11 and 3.13). pytest is needed only for the tests.

## Run it

```bash
cd tools/trade_feed_validator
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

python pipeline.py sample_feed.csv --feed-date 2026-09-28 --out out
python -m pytest -v
```

The sample has times without a date, and the brief says all events happened on the same UTC day. `--feed-date` supplies that day; any date gives the same outcomes. Full ISO-8601 timestamps with an offset need no flag. Output for the sample:

```
line  event_id   status       detail
   2  evt_001    accepted
   3  evt_002    accepted
   4  evt_003    duplicate    duplicate_trade (of evt_002)
   5  evt_004    accepted
   6  evt_005    dead_letter  missing_block_time
   7  evt_006    accepted
   8  evt_007    duplicate    duplicate_trade (of evt_006)
   9  evt_008    dead_letter  block_time_after_ingestion

rows=8 accepted=4 duplicate=2 dead_letter=2 (ratio 0.25)
volume naive        total=  705000 BUY=  540000 SELL=  165000
volume clean        total=  375000 BUY=  330000 SELL=   45000
volume dead_letter  total=  120000 BUY=       0 SELL=  120000
outputs written to out
```

`naive` is what the original loop would have loaded. `report.json` has the same numbers plus reason and flag counts.

Other options: `--max-dead-letter-ratio 0.1` makes the run fail (exit code 1) and withholds `clean_trades.csv` when too many rows are dead-lettered. `--strict-identifiers` requires full-length `0x` hashes and addresses. Tolerances are also flags: `--max-clock-skew`, `--max-ingestion-lag` and `--dedup-horizon`. See `python pipeline.py --help`. A repaired dead letter is replayed by passing it after the original feed: `python pipeline.py sample_feed.csv repaired.csv ...`.

## Data-quality issues in the sample

| # | Rows | Issue | Evidence | Handling |
|---|---|---|---|---|
| 1 | 2, 3 | **Redelivery under a new `event_id`** | `evt_003` matches `evt_002` in tx, block time, wallet, side and amount. It arrived 2 m 41 s after its block, while `evt_001`, `evt_002`, `evt_004`, `evt_006` and `evt_007` took 3–4 s. That pattern fits a retry or replay, and the new `event_id` means a check on `event_id` alone would not catch it. | `duplicate_trade` of `evt_002` |
| 2 | 6, 7 | **Double emission** | `evt_007` matches `evt_006` in every field except `event_id`, including `ingested_at`. That is consistent with one record being emitted twice, for example by a retried batch write or two consumers on one partition. | `duplicate_trade` of `evt_006`. The copies are identical, so keeping the first arrival loses nothing. |
| 3 | 5 | **Missing `block_time`** | `evt_005.block_time` is null. | `missing_block_time` dead letter (see [evt_005](#handling-evt_005)) |
| 4 | 8 | **Block time after ingestion** | `evt_008` was stored at 09:59:50 for a block at 10:10:00, 10 m 10 s before that block existed. At least one of its timestamps is wrong. `ingested_at` also goes backwards: row 8 arrived after row 7 (10:03:15) but is stamped 09:59:50, which points at the ingestion clock. The block time cannot be ruled out either. | `block_time_after_ingestion` dead letter. The block time is checked against the chain and the row replayed. |
| 5 | 7→8 | **Arrival order is not chain order** | The feed header says so, and `ingested_at` is not monotonic. Loading in arrival order hands the table an order that nothing guarantees. | Clean output is sorted by `(block_time, tx_hash, log_index, event_id)`. In a stream, a trade older than one already accepted is flagged `late_arrival`. |
| 6 | all | **The loop itself** | `parse → insert` has no validation, no idempotency key and no quarantine. Re-running a failed load inserts every row again. | Every row gets an outcome, and identity is keyed on the trade rather than the delivery. |
| 7 | all | **Feed contract gaps** | These are not errors in this sample, but they limit what can be checked. Timestamps carry no date, so midnight rollover is ambiguous. There is no `log_index`, so two identical fills in one tx cannot be told apart from a duplicate. There is no price, so VWAP cannot be computed from this feed. Identifiers are shortened. | `--feed-date`, ISO-8601 support, `log_index` used as the key when present, `--strict-identifiers` |

The sample also contains a trap for over-eager deduplication. `evt_001` and `evt_002` have the same wallet, side and amount (0xD4…, BUY, 120,000) but come from different transactions 27 minutes apart. A content-only key such as wallet + side + amount would delete a real trade. The key therefore always includes `tx_hash`, and a test covers this case.

## What each issue corrupts downstream

Sample totals:

| Metric | Original loop | Validated now | After both dead letters are repaired |
|---|---|---|---|
| Trades | 8 | 4 (+2 quarantined) | 6 |
| BUY volume | 540,000 | 330,000 | 330,000 |
| SELL volume | 165,000 | 45,000 | 165,000 |
| Total volume | 705,000 | 375,000 | 495,000 |

- **Duplicates (1, 2)** inflate BUY volume by 210,000, which is 64% of the true 330,000. Total volume comes out 42% too high and trade count 33% too high. VWAP gives a duplicated fill double weight and pulls toward its price. Wallet metrics suffer most:
  - `0xD4…` shows three buys instead of two.
  - `0xF6…` looks net long by 90,000, when it actually bought 90,000 (`evt_006`) and sold 90,000 (`evt_008`), a flat round trip. Round-trip and wash-trading heuristics look for equal, opposite trades by one wallet, so the extra unmatched buy hides that pattern.
  - Duplicates also inflate the co-activity counts that wallet clustering uses to link addresses.
- **Missing block time (3)** has no correct place in a time series. Depending on the engine, the row disappears from `WHERE block_time BETWEEN …` filters, which quietly undercounts, sorts first or last, or turns into the 1970 epoch. The first two outcomes silently understate `0xE5…`'s selling by 30,000. That is 18% of true SELL volume.
- **Impossible timestamp (4)** breaks time ordering. Ordered by ingestion time, `evt_008` (SELL) lands before `evt_006` (BUY), so the round trip reads as sell-then-buy. Its negative ingestion lag (−10 m 10 s) skews latency and freshness metrics. A windowed stream job would assign it to the wrong window or close a window early.
- **Arrival order (5)** breaks any logic that assumes rows arrive sorted: running positions, first/last trade, incremental aggregates that never revisit a closed window.
- **Non-idempotent load (6)** means any retry of the job duplicates the whole batch, which is issue 1 at scale.

## Handling evt_005

**Dead-letter it, repair it from the chain, and replay it.**

- **Dropping it** silently removes a real 30,000 SELL, 18% of true sell volume, and nothing downstream would show that it is missing.
- **Backfilling from `ingested_at`** invents the field that time-based analytics depend on. Row 8 shows that this feed's ingestion timestamps are not reliable.
- **The value can be recovered exactly.** On EVM chains, `eth_getTransactionByHash` returns the transaction's `blockNumber` and `eth_getBlockByNumber` returns that block's `timestamp` ([JSON-RPC API](https://ethereum.org/en/developers/docs/apis/json-rpc/)). The dead letter keeps the raw row and `tx_hash`, and dead-lettered rows do not reserve their identity. The repaired row can therefore be replayed through the same pipeline, and a replay that arrives twice is caught as a duplicate (`test_sample_repaired_dead_letter_can_be_replayed`).

What would change the answer:

- **The `tx_hash` does not exist on chain.** The event is fabricated or corrupt, so drop it and alert on the indexer.
- **There is no chain access, and consumers only need daily aggregates.** Backfill the date only and mark the row as approximate. The brief's same-day guarantee makes that exact at daily grain.
- **Dashboards need low latency.** Publish the trade in an "unknown time" bucket and restate once it is repaired.
- **Many rows miss `block_time` at once.** A broken indexer shard is a systemic fault, so the batch should fail the quality gate (`--max-dead-letter-ratio`) instead of quarantining rows one at a time.

## Catching this class of problems automatically (≤150 words)

Treat the feed as a versioned data contract that is checked in code at ingestion, not by analysts later:

1. Validate every record for schema, nullability, ranges and cross-field invariants such as `block_time ≤ ingested_at`. Failures go to a dead-letter queue with reason codes and are never dropped silently.
2. Make loads idempotent by upserting on the on-chain identity `(chain, tx_hash, log_index)`, never on delivery IDs.
3. Emit per-batch quality metrics (dead-letter and duplicate ratios by reason, ingestion-lag percentiles, rows per block) and alert on thresholds. A quality gate blocks publishing when a batch breaches them.
4. Reconcile on a schedule: compare counts and volumes per block range against a node or second indexer to catch rows that never arrived.
5. Run all of this in CI against a corpus of known-bad fixtures, including this sample.

## Design

**Identity.** An event's identity is the trade, not the delivery. The natural key is `(tx_hash, log_index)` when the feed provides `log_index`, and `(tx_hash, wallet, side, amount)` otherwise, with `block_time` required to agree. Hex identifiers are lower-cased first: hex values are case-insensitive, and mixed case in an EVM address only encodes a checksum ([EIP-55](https://eips.ethereum.org/EIPS/eip-55)). Checks run in this order:

1. Same `event_id` and same payload → `duplicate_event_id`. Same `event_id` with a different payload → `conflicting_event_id`.
2. Same `tx_hash` in a different block → `conflicting_block_time`. A transaction is included in exactly one block, so this is a reorg or corruption. It is checked before the natural key, so a disagreeing copy is surfaced rather than dropped as a duplicate.
3. Same natural key → `duplicate_trade`, or `conflicting_payload` if a `log_index` key matches but other fields differ.

The `event_id` of a dropped duplicate is reserved, so it cannot be reused for a different trade. The `event_id` of a dead letter is not reserved, so the repaired row can be replayed.

**Reason codes.**

| Outcome | Codes |
|---|---|
| dead letter, bad row | `malformed_row`, `missing_<field>`, `invalid_<field>` (all field errors reported together) |
| dead letter, bad time | `block_time_after_ingestion` (beyond `--max-clock-skew`, default 30 s), `ingested_at_in_future`, `block_time_before_min` (before 2009-01-03, the [Bitcoin genesis block](https://en.bitcoin.it/wiki/Genesis_block), which catches epoch-0 placeholders), `beyond_dedup_horizon` |
| dead letter, conflict | `conflicting_event_id`, `conflicting_block_time`, `conflicting_payload` |
| duplicate | `duplicate_event_id`, `duplicate_trade` |
| flags on accepted rows | `high_ingestion_lag` (above `--max-ingestion-lag`, default 60 s), `late_arrival` |

Amounts must be plain positive decimals no larger than 2²⁵⁶−1. That is the ceiling of an ERC-20 `uint256` balance in base units ([EIP-20](https://eips.ethereum.org/EIPS/eip-20)), so a larger value cannot be a real EVM token amount in any unit. NaN, infinity, signs, thousands separators and naive (offset-less) timestamps are rejected rather than guessed.

**Bounded state.** `TradeFeedValidator` is a streaming processor that keeps its de-duplication state only for `--dedup-horizon` (default 24 h) of block time behind the newest accepted trade. That keeps memory flat on an unbounded feed. A record older than the horizon cannot be proven unique, so it is dead-lettered (`beyond_dedup_horizon`) and never accepted blindly. For a batch job the horizon can be set to cover the whole batch.

**Input and output.** Rows are read with `csv.reader`, not `DictReader`, so rows with too many or too few fields are dead-lettered with every value kept. A missing or repeated column, an empty file or non-UTF-8 input rejects the whole feed (exit code 2). Extra columns are allowed. Each output file is written to a temporary file and moved into place with `os.replace`. When the quality gate fails, any `clean_trades.csv` from an earlier run is deleted so it cannot be mistaken for this run's output.

**Known limits.**

- Replacement is atomic per file, not across the set of outputs.
- In streaming mode, the first of two conflicting records has already been accepted when the conflict is seen. The conflict is dead-lettered with `related_event` pointing at the first record so it can be reconciled.
- The repair step (the chain lookup) is out of scope. The interface to it is the dead-letter file and replay.

## Files

```
sample_feed.csv         the feed from the issue
validator.py            parsing, validation, de-duplication (TradeFeedValidator)
pipeline.py             CLI: read CSVs, run the validator, publish outputs and report
tests/test_validator.py rule-level tests, one or more per reason code
tests/test_pipeline.py  end-to-end tests on the sample, malformed input, quality gate
```
