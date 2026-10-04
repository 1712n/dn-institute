# Trade feed validator (Go)

This command validates a CSV trade feed before analytics ingestion. Valid rows
are emitted in `block_time` order. Unsafe rows are preserved in a dead-letter
CSV with machine-readable reason codes; they are never silently inserted.

## Issues in the sample

| Rows | Issue | Downstream impact | Handling |
|---|---|---|---|
| `evt_002`/`evt_003` | The same trade was delivered twice under different event IDs; the later copy has a different ingestion time. | Double-counts 120,000 in volume, biases VWAP (when price is present), and inflates wallet activity. | Keep the first valid occurrence, send `evt_003` to the DLQ as `duplicate_trade`. |
| `evt_006`/`evt_007` | Duplicate trade delivered at the same ingestion time. | Double-counts 90,000 and inflates wallet activity/trade count. | Keep `evt_006`, send `evt_007` to the DLQ as `duplicate_trade`. |
| `evt_005` | Missing `block_time`. | Cannot assign the trade to a reliable time bucket or chain order; substituting ingestion time corrupts candles, windows, latency, and time-based wallet analysis. | Send to the DLQ as `missing_block_time`; do not include it in analytics. |
| `evt_008` | `ingested_at` is 10m10s before `block_time`. | Produces negative ingestion latency and violates causal/time-ordering assumptions; it can place data in the wrong window. | Send to the DLQ as `block_time_after_ingested_at`. |
| Feed contract | Arrival order is not guaranteed to be chain order. | Stream-order windows can produce incorrect candles, balances, and “first/last” wallet activity. | Sort accepted batch output by `block_time`. A streaming deployment should use event-time watermarks and an allowed-lateness policy. |

`evt_001` and `evt_002` are **not** duplicates: matching wallet, side, and amount
does not identify a trade because their transaction hashes differ.

The challenge feed has no log index. The validator therefore uses
`tx_hash + block_time + wallet + side + amount` as its best available canonical
trade key. A production indexer should provide `(chain_id, tx_hash, log_index)`;
that stable source key should replace the fallback fingerprint, because one
transaction can legitimately contain multiple identical-looking trade logs.

### Why `evt_005` goes to a DLQ

Dropping it loses a real trade without an audit trail, while using
`ingested_at` invents chain time and silently contaminates analytics. A DLQ is
therefore the safest default: it isolates the row, records the reason, and
allows replay. I would backfill and replay it if an authoritative source (node,
block/transaction receipt, or indexer API) can recover the block timestamp from
a stable transaction identity. I would drop it only after a retention period
if recovery is impossible and the documented completeness trade-off is
acceptable.

## Run

Requirements: Go 1.22 or newer. There are no third-party dependencies.

```sh
cd tools/trade_feed_validator
go mod download
go run . \
	-input sample_feed.csv \
	-output-dir output
```

Expected summary:

```text
processed=8 accepted=4 rejected=4 output_dir=output
```

The output directory is created automatically and contains:

- `valid_trades.csv` — rows safe for analytics ingestion;
- `rejected_events.csv` — original rejected rows, source row numbers, issue
  codes, and explanations;
- `validation_report.json` — machine-readable counts by issue, rejection rate,
  parseable input/accepted/rejected amounts, and output names.

## Test

```sh
cd tools/trade_feed_validator
go test ./...
```

For verbose output suitable for the pull request description:

```sh
go test -v ./...
```

## General prevention (145 words)

Define a versioned data contract at ingestion: required fields, types, enums,
ranges, timestamp causality, and a source-stable idempotency key such as
`(chain_id, tx_hash, log_index)`. Validate every event against it before the
analytics table, writing failures to a replayable DLQ rather than silently
coercing or dropping them. Make the sink idempotent with a database uniqueness
constraint, since process-local deduplication does not survive restarts or
multiple workers. Process by event time with watermarks and an explicit
late-arrival policy. Continuously publish quality metrics—rejection rate by
reason, duplicate rate, missingness, ingestion-latency distribution, and
accepted input/output counts—and alert on both absolute thresholds and changes
from a rolling baseline. Reconcile aggregates and row counts against the source
for each completed block/window. Keep raw immutable input so rules can be
changed and history replayed. Run contract and anomaly checks in CI on fixtures,
then canary rule changes before enforcing them in production.

## Pull request checklist

- Paste the output of `go test -v ./...` into the PR description.
- Include `Solves #1209`.
- Request a review from `@argeter`.
