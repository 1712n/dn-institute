# Trade Feed Validator

A validator for trade event feeds from blockchain indexers. It checks each event before it reaches analytics, so volume, VWAP and wallet-activity metrics are computed only from rows that pass.

Built for [#1209](https://github.com/1712n/dn-institute/issues/1209), where an existing pipeline wrote indexer events straight to analytics without any checks. In the sample feed, the validator finds duplicate events, a missing block time and an impossible timestamp, and quarantines each for resolution against the chain. The underlying problem is that nothing defines what an event is, so this README also proposes a data contract; the validator enforces the schema the feed has today.

## Quick start

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
cd tools/trade_feed_validator
uv sync                                                  # install dependencies (pytest)
uv run python -m trade_feed_validator sample_feed.csv   # run the pipeline, writes out/
uv run pytest                                            # run the tests
```

Running the pipeline on the sample prints:

```
sample_feed.csv: 8 rows
  clean        7
  quarantined  0
  dropped      1
Written to out: clean.csv, quarantine.csv, dropped.csv
```

Usage: `python -m trade_feed_validator FEED [--out-dir DIR]` (default `out`).

## Problems with the inherited setup

The main problem with the inherited setup is that there is no contract defining what an event is. Most issues in the sample follow from it:

1. **"Event" isn't defined.** It can't simply be a transaction: in DeFi protocols one transaction can contain several trades, such as batch settlements across wallets, split routes and multi-hop swaps. Required content (price, asset, units, full timestamps) isn't defined either.

2. **No unique event identifier.** `event_id` appears to identify an ingestion, not a trade: a likely redelivery (evt_003) carries a new id. `tx_hash` can't identify an event, per point 1.

3. **No total ordering.** `block_time` ties within a block, within a transaction and across wallets. Block number orders only blocks, not transactions or trades within them.

As a result, duplicates can't be told apart from legitimate trades in the same transaction. Separately, the pipeline doesn't validate rows at all, so these and other defects (like the skewed clock in evt_008) reach analytics unchecked.

## Data-quality issues

Each issue ends with its handling. *Quarantined* rows go to `quarantine.csv`, which serves as the dead-letter queue; *loaded* means written to `clean.csv`.

**1. Duplicate events** (evt_002/evt_003, evt_006/evt_007)
Each pair is the same trade (transaction, wallet, side, amount, time) with a different `event_id`.
- evt_003 arrived well after evt_002, much later than the usual ingestion lag, so it's likely a redelivery (retry or reorg reprocessing).
- evt_007 arrived together with evt_006, which also fits two legitimate trades in one transaction. Without an event identifier this can't be decided.

**Handling:** the first record is loaded; later records matching it on transaction, wallet, side, amount and block time are quarantined as suspected duplicates, not dropped. A row whose block time is missing or impossible is matched only once the chain has supplied the real one. Decoding the transaction afresh from chain data resolves them: if it contains fewer matching trades than there are records, the extra records are duplicates (dropped); otherwise they're separate trades (loaded).
Once the contract defines an event identifier, loads become idempotent upserts on it, so retries and backfills can't create duplicates; redeliveries are still counted, so a misbehaving source stays visible.

**2. Missing required value** (evt_005)
`block_time` is null, so the trade can't be placed in time. It's either missing or the transaction was never confirmed; the chain can tell which via `tx_hash`.

**Handling:** quarantined and backfilled from the chain; see [Handling evt_005](#handling-evt_005).

**3. Invariant violation** (evt_008)
`ingested_at` is earlier than `block_time`: the event was ingested before it happened on-chain, which is impossible. Most likely the ingest clock is skewed, which also makes `ingested_at` unreliable for the whole feed.

**Handling:** quarantined, and `block_time` is verified on-chain. If it matches, the trade is loaded with `ingested_at` flagged as unreliable. If not, `block_time` is corrected from the chain, and `ingested_at` is still flagged if it remains earlier. If the transaction isn't on chain, the row is dropped.

## Downstream impact

### From the undefined event

**Missing trade attributes**
VWAP and value-based metrics (notional, USD volume) can't be computed from the feed, and joining external prices by time imports its timestamp problems. Without asset and units, summed volume assumes every trade is the same asset at the same scale.

**Incomplete timestamps**
Day assignment depends on an external assumption, so trades near midnight or backfilled from earlier days can land on the wrong day, corrupting daily volume and daily active wallets.

**Undefined total ordering**
Sequence-dependent metrics are undefined for tied events: open/close and last price, position reconstruction, detection of patterns such as sandwiches. Queries can order tied rows differently, so results aren't reproducible, and an arbitrary tie-break invents an order where trades were simultaneous by design (batch settlement).

### From issues in the sample

**1. Duplicate events**
Additive metrics count the trade twice (volume, trade counts, buy/sell pressure), and per-wallet activity is overstated, distorting rankings, whale thresholds and the features used for wallet clustering and bot detection. Removing duplicates isn't safe either: if a pair is really two trades, dropping one understates volume. The error has unknown direction.

**2. Missing required value**
The trade falls out of every time window, so intraday aggregates miss it and daily totals stop reconciling with them. The wallet's sequence (first/last activity, time between trades) breaks.

**3. Invariant violation**
Lag and freshness monitoring report impossible values and can mask real delays. Incremental loads using `ingested_at` as a watermark can silently skip the row, and anything windowed by `ingested_at` misplaces the trade and can reverse a wallet's sequence.

## Handling evt_005

**Options**
- **Drop:** simple, and analytics stays clean. But it silently loses a probably-real trade and hides the upstream defect. Irreversible.
- **Estimated backfill** (from `ingested_at` or neighboring rows): loads immediately. But the time is a guess presented as fact; the feed's clock is unreliable (evt_008), and if the transaction never confirmed, it inserts a trade that never happened.
- **Authoritative backfill** (look up `tx_hash` on-chain): exact, and verifies the transaction exists and is final. But it needs chain access and adds latency; done inline, it ties the pipeline's availability to the chain node.
- **Dead-letter queue:** nothing incorrect is loaded, and the row is preserved and resolvable later. But totals are incomplete until resolution, and without monitoring and a deadline it becomes a slow drop. On its own it decides nothing.

**Decision: dead-letter queue, resolved by authoritative backfill.**
The queue keeps guesses out of analytics; the chain lookup supplies the exact value without blocking the pipeline.
- **Confirmed and final:** fill `block_time`, re-run the checks (invariant, duplicates), then load.
- **Not found, reverted or reorged out:** drop, with the reason recorded.

**What would change the answer**
The approach depends on the context it runs in; if that changes, so does the choice.
- **No authoritative source** (no chain access, or an off-chain source such as an exchange): the queue can't resolve anything. Request redelivery from the source, and drop after a deadline.
- **Freshness matters more than exactness** (real-time dashboards): estimated backfill becomes acceptable, provided values are flagged as estimates and corrected later.
- **Exactness matters more than freshness** (reporting, compliance): never load estimates; keep rows queued until resolved, even if totals stay incomplete longer.

## Catching this class of problems

The root problem is that no contract defines what an event is. I would add an explicit **data contract** between indexer and analytics, enforced by the feed validator.

The contract defines: required fields, types and units, the fields that identify an event, its block reference and ordering position, and the invariants it must satisfy. Each part enables a check:

- **Schema** → catches missing required values (evt_005).
- **Identity** → flags repeats of an existing event (evt_003, evt_007).
- **Ordering** → requires a position for every event.
- **Invariants** → catches impossible values, e.g. `ingested_at < block_time` (evt_008).

Violations are then handled at three levels:

- **Per row:** quarantined with the raw record and a reason code, so every decision is traceable; resolved automatically where possible.
- **Per batch:** spikes in violation rates signal upstream faults and raise alerts.
- **Per feed:** events that never arrive escape row checks; reconciliation against an independent source catches them.

## How the validator works

Each row goes through three stages, in arrival order:

1. **Parse** (`parsing.py`): the row becomes a typed event, or is quarantined with every problem found. Timestamps are either ISO 8601 with a timezone, converted to UTC, or a time of day (`HH:MM:SS`) taken as UTC; `null` or an empty field counts as missing. A header without the seven schema columns, or with a repeated column, stops the run.
2. **Check** (`checks.py`, `pipeline.py`): the invariant, then suspected duplicates. Rows with any violation are quarantined; the rest are clean.
3. **Resolve** (`resolution.py`): quarantined rows are checked through the `ChainResolver` interface (transaction facts from the chain, trade counts from decoding the transaction afresh) and are loaded, dropped or left in quarantine. The run uses `DummyChainResolver` (`dummy_resolver.py`), whose answers are synthetic; see [Assumptions](#assumptions).

### Output

All three files are written on every successful run, even when empty.

| File | Contents |
|---|---|
| `clean.csv` | Loaded events: schema columns (UTC timestamps) and `flags`. Rows clean on arrival come first, then rows loaded by resolution. |
| `quarantine.csv` | `line` in the source file, schema columns as read, `reasons`, `details`, `flags`. |
| `dropped.csv` | `line`, schema columns as read, `drop_reason`. |

Input columns outside the schema aren't copied; `line` points to the full source row. `reasons` list what is still unresolved; `flags` record what resolution changed or verified. If the feed can't be read, or is itself one of the output files, the run exits with code 1 and writes nothing.

### Reason codes

| Code | Where | Meaning |
|---|---|---|
| `malformed_row` | reasons | Row has more or fewer fields than the header. |
| `invalid_timestamp` | reasons | Neither ISO 8601 with a timezone nor a valid `HH:MM:SS` time, or out of range in UTC. |
| `invalid_amount` | reasons | Not a positive number in plain decimal notation (`1e5` is rejected). |
| `invalid_side` | reasons | Not `BUY` or `SELL`. |
| `missing_required_value` | reasons | Empty or `null`. Only a missing `block_time` can be resolved. |
| `suspected_duplicate` | reasons | Same transaction, wallet, side, amount and block time as an earlier row. |
| `ingested_before_block` | reasons | `ingested_at` is earlier than `block_time`. |
| `block_time_backfilled` | flags | Missing `block_time` filled from the chain. |
| `block_time_corrected` | flags | `block_time` replaced with the chain's value. |
| `ingested_at_unreliable` | flags | `ingested_at` is earlier than the verified `block_time`. |
| `confirmed_distinct_trade` | flags | Decoding the transaction afresh confirms a separate trade, not a duplicate. |
| `tx_not_found` | drop_reason | Transaction not on chain, reverted or reorged out. |
| `duplicate_confirmed` | drop_reason | More records than matching trades in the transaction. |

## Scope

**Implemented:** parsing and the schema check for the seven columns, the suspected-duplicate check, the `ingested_at ≥ block_time` invariant, per-row quarantine with line, raw values and reason codes, and resolution of every sample issue behind the chain resolver interface.

**Stubbed:** the chain resolver. The run uses `DummyChainResolver`, whose answers are synthetic and chosen to fit the sample; the tests use a mock resolver (`MockChainResolver`) for every outcome. Connecting real sources means implementing `lookup_tx` (a chain query) and `count_matching_trades` (the indexer's decoding of a single transaction).

**Proposed, not implemented:** the data contract, the ordering check, idempotent writes on an event identifier, per-batch alerting and per-feed reconciliation.

## Assumptions

- The sample gives times only, and `sample_feed.csv` keeps them as given. A feed of times without dates is taken to cover a single day, as the issue states, so an event crossing midnight can't be represented; `clean.csv` writes such times back without a date.
- `null` is kept as in the sample; an empty field is treated the same way.
- Wallets and tx hashes stay in their shortened form and are compared exactly as written.
- The run's chain answers are synthetic, made up to fit the sample rather than derived from it: `0xaa4` (evt_005) is in a block at 09:58:27; `0xaa6` (evt_008) is in a block at 10:10:00, as the feed says; `0xaa2` holds one trade matching evt_003, and `0xaa5` holds two matching evt_007.

## Known limitations

- If the transaction has no matching trade at all, the later records are dropped, but the first is already in `clean.csv` and isn't withdrawn.
- When the feed can't be read, output from an earlier run stays in place; only the exit code reports the failure.
