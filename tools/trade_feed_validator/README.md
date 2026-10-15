# Trade Feed Validator

Validates a trade event feed before it is loaded into analytics. Each row goes
to one of two files:

- `output/clean.csv` — events that are safe to load;
- `output/dead_letter.csv` — rejected events with their original values and the
  reason, so they can be fixed and replayed.

## Install, run, test

Requires Go 1.22+. No third-party dependencies.

```bash
cd tools/trade_feed_validator
go mod download            # nothing to download, verifies the module
go run . -date 2026-01-01 sample_feed.csv   # writes output/clean.csv and output/dead_letter.csv
go test ./... -v
```

The sample feed only has times of day and no calendar date, so `-date` is
required: it is the UTC day the feed belongs to (the task gives none, so
2026-01-01 above is only an example). Without it the run stops instead of
guessing a day. Feeds with full RFC 3339 timestamps don't need `-date`.
All times get the same date, so a time-only
feed that crosses midnight would wrongly flag trades as
`block_time_after_ingested_at` — such feeds should use full RFC 3339
timestamps (`2026-03-05T23:59:58Z`), which are also accepted.


### Test output

```
$ go test ./... -v
?   	trade_feed_validator	[no test files]
?   	trade_feed_validator/models	[no test files]
ok  	trade_feed_validator/pipeline	0.581s
ok  	trade_feed_validator/validator	0.782s
```

<details>
<summary>Full verbose output (22 tests, 8 subtests, all passing)</summary>

```
?   	trade_feed_validator	[no test files]
?   	trade_feed_validator/models	[no test files]
=== RUN   TestSampleFeed
--- PASS: TestSampleFeed (0.00s)
=== RUN   TestResultDoesNotDependOnRunDate
--- PASS: TestResultDoesNotDependOnRunDate (0.00s)
=== RUN   TestTimesAreAnchoredToFeedDate
--- PASS: TestTimesAreAnchoredToFeedDate (0.00s)
=== RUN   TestRFC3339TimestampsAreAccepted
--- PASS: TestRFC3339TimestampsAreAccepted (0.00s)
=== RUN   TestColumnsAreMatchedByName
--- PASS: TestColumnsAreMatchedByName (0.00s)
=== RUN   TestMissingHeaderColumnIsAnError
--- PASS: TestMissingHeaderColumnIsAnError (0.00s)
=== RUN   TestBadRowsGoToDeadLetterWithoutStoppingThePipeline
--- PASS: TestBadRowsGoToDeadLetterWithoutStoppingThePipeline (0.00s)
=== RUN   TestInvalidCSVRowIsDeadLetteredAndProcessingContinues
--- PASS: TestInvalidCSVRowIsDeadLetteredAndProcessingContinues (0.00s)
=== RUN   TestNullVariantsAreTreatedAsMissing
--- PASS: TestNullVariantsAreTreatedAsMissing (0.00s)
=== RUN   TestNullEventIDIsMissingField
--- PASS: TestNullEventIDIsMissingField (0.00s)
=== RUN   TestWriteOutputs
--- PASS: TestWriteOutputs (0.00s)
PASS
ok  	trade_feed_validator/pipeline	0.581s
=== RUN   TestValidEventIsAccepted
--- PASS: TestValidEventIsAccepted (0.00s)
=== RUN   TestMissingBlockTime
--- PASS: TestMissingBlockTime (0.00s)
=== RUN   TestBlockTimeAfterIngestedAt
--- PASS: TestBlockTimeAfterIngestedAt (0.00s)
=== RUN   TestBlockTimeEqualToIngestedAtIsAccepted
--- PASS: TestBlockTimeEqualToIngestedAtIsAccepted (0.00s)
=== RUN   TestRedeliveredDuplicate
--- PASS: TestRedeliveredDuplicate (0.00s)
=== RUN   TestExactDuplicate
--- PASS: TestExactDuplicate (0.00s)
=== RUN   TestSameEventIDTwiceIsRejected
--- PASS: TestSameEventIDTwiceIsRejected (0.00s)
=== RUN   TestDifferentTradesInSameTransactionAreKept
--- PASS: TestDifferentTradesInSameTransactionAreKept (0.00s)
=== RUN   TestSameContentDifferentTxIsKept
--- PASS: TestSameContentDifferentTxIsKept (0.00s)
=== RUN   TestRejectedEventDoesNotBlockBackfilledReplay
--- PASS: TestRejectedEventDoesNotBlockBackfilledReplay (0.00s)
=== RUN   TestFieldChecks
=== RUN   TestFieldChecks/missing_tx_hash
=== RUN   TestFieldChecks/missing_wallet
=== RUN   TestFieldChecks/missing_event_id
=== RUN   TestFieldChecks/missing_ingested_at
=== RUN   TestFieldChecks/unknown_side
=== RUN   TestFieldChecks/zero_amount
=== RUN   TestFieldChecks/negative_amount
=== RUN   TestFieldChecks/several_problems_at_once
--- PASS: TestFieldChecks (0.00s)
    --- PASS: TestFieldChecks/missing_tx_hash (0.00s)
    --- PASS: TestFieldChecks/missing_wallet (0.00s)
    --- PASS: TestFieldChecks/missing_event_id (0.00s)
    --- PASS: TestFieldChecks/missing_ingested_at (0.00s)
    --- PASS: TestFieldChecks/unknown_side (0.00s)
    --- PASS: TestFieldChecks/zero_amount (0.00s)
    --- PASS: TestFieldChecks/negative_amount (0.00s)
    --- PASS: TestFieldChecks/several_problems_at_once (0.00s)
PASS
ok  	trade_feed_validator/validator	0.782s
```

</details>

## Data-quality issues

| # | Issue | Rows | Error code |
|---|-------|------|------------|
| 1 | Same trade delivered twice, at different times | evt_002 / **evt_003** | `redelivered_duplicate` |
| 2 | Exact duplicate (identical except `event_id`) | evt_006 / **evt_007** | `exact_duplicate` |
| 3 | `block_time` is null | **evt_005** | `missing_block_time` |
| 4 | `block_time` is later than `ingested_at` | **evt_008** | `block_time_after_ingested_at` |

Bold rows are rejected; the first copy of each duplicate is kept. evt_001 and
evt_002 are not duplicates: same wallet and amount, but different transactions.

The feed has no `log_index`, so duplicates are detected by trade content
(tx_hash, wallet, side, amount, block_time). This is ambiguous: two genuinely
identical fills in one transaction would be treated as a duplicate. When the
feed carries `log_index`, `(tx_hash, log_index)` should be the key instead.

## Downstream impact

Loading the feed as-is gives a total volume of 705 000; after validation it is
375 000 (405 000 once evt_005 is backfilled).

1. **evt_003 (redelivery)** — the indexer re-sent the same trade (same tx, wallet,
   amount, block_time; later `ingested_at`). Volume and VWAP weight are doubled:
   `0xD4…` shows 360 000 BUY instead of 240 000, and its trade count is inflated,
   which skews wallet activity and clustering.
2. **evt_007 (exact duplicate)** — even `ingested_at` is identical. This hints at
   the same record being written twice (e.g. a batch replay) rather than a later
   re-delivery, but the feed has no provenance to confirm where it came from, so
   it gets its own code to make it easy to investigate separately. Same effect:
   `0xF6…` shows 180 000 BUY instead of 90 000.
3. **evt_005 (null block_time)** — the trade cannot be placed in any time bucket.
   Time-windowed volume and VWAP either skip it or, if `null` is replaced by a
   default, put it in the wrong window. Ordering by chain time breaks.
4. **evt_008 (block_time after ingested_at)** — we "ingested" the trade ten
   minutes before it happened, so one timestamp is wrong (its `ingested_at`
   also goes backwards vs. the previous row, suggesting clock skew). Indexer lag
   becomes negative, freshness monitoring and late-data watermarks break, and
   the trade may land in the wrong window. Since we can't tell which timestamp
   is right, it is dead-lettered.

## Handling evt_005: dead-letter queue

evt_005 goes to `dead_letter.csv` with its raw values and code
`missing_block_time`. It is neither loaded nor dropped.

- **Not drop:** the trade is probably real; dropping it silently loses 30 000 of
  `0xE5…` SELL volume.
- **Not backfill with a guess:** `ingested_at` is not chain time; guessing puts
  the trade in a possibly wrong window without anyone noticing.
- **Dead-letter:** nothing is lost and nothing wrong is loaded. The `tx_hash` is
  present, so the real `block_time` can be fetched from an RPC node and the row
  replayed. The validator only remembers accepted events, so the replay is not
  rejected as a duplicate.
- In real life, depending on the number of records being processed and the percentage 
  of such cases, I would either immediately re-query the blockchain, or create a queue
  in a message broker for such cases to re-query the blockchain, or store them in a 
   separate table for re-querying the data source.

**What would change the answer:**
- RPC access inside the pipeline → backfill from the chain automatically.
- The transaction doesn't exist on-chain → drop it, it isn't a real trade.
- A metric that doesn't need time (e.g. all-time volume or trade count per
  wallet) → load it with a `missing_block_time` flag and include it there, but
  keep it out of every time-windowed metric (hourly volume, VWAP windows).
- The metric window is already published and restatements aren't allowed → keep
  it in the queue and report it as a known gap.

## General practice

Treat the feed as a contract and enforce it at the boundary, not in dashboards.
1) Schema check on every event: required fields, types, allowed values, UTC
timestamps. 
2) Idempotent loading: write with a natural key (chain, tx_hash,
log_index) and upsert instead of insert, so redeliveries cannot double-count.
3) Invariant checks such as `block_time <= ingested_at` and bounded indexer lag.
4) A dead-letter table with reason codes and a replay job, so nothing is
silently dropped or silently loaded. 
5) Per-batch quality metrics — reject rate
by code, duplicate rate, null rate, lag — with alerts on thresholds.
6) Reconciliation: compare daily volume and trade count against an independent
source (an RPC node or a second indexer) before metrics are published.
