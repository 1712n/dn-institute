# Trade feed validator

Go 1.27+. Uses only the standard library.

Run from this directory:

```powershell
go mod download
go run ./cmd/validator
go run ./cmd/validator path/to/feed.csv
go test ./...
```

The CLI writes JSON to stdout: accepted trades, quarantined source rows with reasons, skipped duplicates, and issue details. Structural errors (file, CSV, or header) exit non-zero; row-level issues are returned in the report.

## Findings

Line numbers include the header (line 1).

| Line | Issue | Impact | Handling |
| --- | --- | --- | --- |
| 4 (`evt_003`) | Duplicate of `evt_002` | Inflates volume and wallet activity | Skip replay |
| 6 (`evt_005`) | Missing `block_time` | Breaks time buckets and ordering | Quarantine; backfill from the authoritative indexer, then replay |
| 8 (`evt_007`) | Duplicate of `evt_006` | Inflates volume and wallet activity | Skip replay |
| 9 (`evt_008`) | Ingestion precedes block time | Invalid ordering and freshness metrics | Quarantine pending source correction |

For this sample, duplicates are matched by `(tx_hash, block_time, wallet, side, amount)`. In production, use a unique event/log index because one transaction can contain multiple trades.

## Prevention

Validate a versioned schema at ingestion, including required fields, types, ranges, and timestamp relationships. Use stable event identifiers and source offsets for idempotency. Preserve raw input, route invalid records to a dead-letter store with a reason, and support safe replay after correction. Monitor freshness, duplicate/null rates, and volume anomalies with alerts; compare aggregates with independent source totals. Test contracts with representative fixtures and monitor failures by source and schema version.
