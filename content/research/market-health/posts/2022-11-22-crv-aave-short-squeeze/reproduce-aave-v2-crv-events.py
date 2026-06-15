#!/usr/bin/env python3
"""Fetch and decode Aave v2 CRV Borrow/LiquidationCall events for the Nov 2022 CRV squeeze.

The script uses Ethereum JSON-RPC only (default: https://ethereum.publicnode.com),
decodes Aave v2 LendingPool logs, and writes two local evidence files:

- aave-v2-crv-account-events.csv
- aave-v2-crv-onchain-summary.json

Rerunning this script requires live Ethereum JSON-RPC access; the checked-in CSV
and JSON files are the local evidence artifacts used by the article.
"""
from __future__ import annotations

import csv
import json
import os
import time
import urllib.request
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_RPC_URL = "https://ethereum.publicnode.com"
RPC_URL = os.environ.get("ETH_RPC_URL", DEFAULT_RPC_URL)
LENDING_POOL = "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9"
ACCOUNT = "0x57e04786e231af3343562c062e0d058f25dace9e"
CRV = "0xD533a949740bb3306d119CC777fa900bA034cd52"
USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

# Aave v2 LendingPool event signatures (keccak256 topics):
# Borrow(address,address,address,uint256,uint256,uint256,uint16)
# Repay(address,address,address,uint256)
# LiquidationCall(address,address,address,uint256,uint256,address,bool)
BORROW_TOPIC = "0xc6a898309e823ee50bac64e45ca8adba6690e99e7841c45d754e2a38e9019d9b"
REPAY_TOPIC = "0x4cdde6e09bb755c9a5589ebaec640bbfedff1362d4b255ebf8339782b9942faa"
LIQUIDATION_TOPIC = "0xe413a321e8681d831f4dbccbca790d2952b56f977908e45be37335533e005286"

NOV_1_2022 = int(datetime(2022, 11, 1, tzinfo=timezone.utc).timestamp())
NOV_21_2022 = int(datetime(2022, 11, 21, tzinfo=timezone.utc).timestamp())
NOV_24_2022 = int(datetime(2022, 11, 24, tzinfo=timezone.utc).timestamp())


def rpc(method: str, params: list):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = urllib.request.Request(
        RPC_URL,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "dn-institute-evidence-script/1.0"},
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=90) as response:
                out = json.loads(response.read())
            if "error" in out:
                raise RuntimeError(out["error"])
            return out["result"]
        except Exception:
            if attempt == 3:
                raise
            time.sleep(1.5 * (attempt + 1))


def block_timestamp(block_number: int) -> int:
    block = rpc("eth_getBlockByNumber", [hex(block_number), False])
    return int(block["timestamp"], 16)


def block_before(timestamp: int) -> int:
    lo = 15_000_000
    hi = int(rpc("eth_blockNumber", []), 16)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if block_timestamp(mid) <= timestamp:
            lo = mid
        else:
            hi = mid - 1
    return lo


def padded_address(address: str) -> str:
    return "0x" + "0" * 24 + address[2:].lower()


def address_from_word(word: str) -> str:
    return "0x" + word[-40:]


def words(data: str) -> list[str]:
    raw = data[2:]
    return [raw[i : i + 64] for i in range(0, len(raw), 64)]


def decimal_units(value: int, decimals: int) -> str:
    whole = value // 10**decimals
    frac = value % 10**decimals
    if frac == 0:
        return str(whole)
    return f"{whole}.{str(frac).zfill(decimals).rstrip('0')}"


def iso_utc(block_number: int, cache: dict[int, str]) -> str:
    if block_number not in cache:
        cache[block_number] = datetime.fromtimestamp(block_timestamp(block_number), tz=timezone.utc).isoformat().replace("+00:00", "Z")
    return cache[block_number]


def summary_rpc_url() -> str:
    return RPC_URL if RPC_URL == DEFAULT_RPC_URL else "<redacted ETH_RPC_URL>"


def get_logs(from_block: int, to_block: int, topics: list, chunk_size: int = 50_000) -> list[dict]:
    logs: list[dict] = []
    for start in range(from_block, to_block + 1, chunk_size):
        end = min(start + chunk_size - 1, to_block)
        result = rpc(
            "eth_getLogs",
            [
                {
                    "address": LENDING_POOL,
                    "fromBlock": hex(start),
                    "toBlock": hex(end),
                    "topics": topics,
                }
            ],
        )
        if not isinstance(result, list):
            raise RuntimeError(f"eth_getLogs returned non-list result: {result!r}")
        logs.extend(result)
    return logs


def receipt_logs_for_candidate_transactions(candidate_logs: list[dict], topic0: str) -> list[dict]:
    """Return canonical receipt logs for the tx hashes discovered via eth_getLogs.

    Some public JSON-RPC gateways can return unusual logIndex values directly from
    eth_getLogs. Fetching receipts for the candidate tx hashes keeps the evidence
    tied to canonical transaction receipts while still using eth_getLogs for public
    discovery.
    """
    logs: list[dict] = []
    seen_tx_hashes = sorted({log["transactionHash"] for log in candidate_logs})
    for tx_hash in seen_tx_hashes:
        receipt = rpc("eth_getTransactionReceipt", [tx_hash])
        if not isinstance(receipt, dict) or receipt.get("status") != "0x1":
            continue
        for log in receipt.get("logs", []):
            if log.get("address", "").lower() == LENDING_POOL.lower() and log.get("topics", [None])[0] == topic0:
                logs.append(log)
    return logs


def main() -> None:
    borrow_start = block_before(NOV_1_2022)
    event_start = block_before(NOV_21_2022)
    event_end = block_before(NOV_24_2022)
    ts_cache: dict[int, str] = {}
    rows: list[dict[str, str]] = []

    # Borrow.user is in data word 0; reserve and onBehalfOf are indexed topics.
    borrow_candidates = get_logs(borrow_start, event_end, [BORROW_TOPIC, padded_address(CRV)])
    borrow_logs = receipt_logs_for_candidate_transactions(borrow_candidates, BORROW_TOPIC)
    for log in borrow_logs:
        if log["topics"][1].lower() != padded_address(CRV):
            continue
        decoded = words(log["data"])
        user = address_from_word(decoded[0])
        on_behalf_of = address_from_word(log["topics"][2])
        if user.lower() != ACCOUNT.lower() and on_behalf_of.lower() != ACCOUNT.lower():
            continue
        block_number = int(log["blockNumber"], 16)
        amount_raw = int(decoded[1], 16)
        rows.append(
            {
                "event_type": "Borrow",
                "block_number": str(block_number),
                "block_timestamp_utc": iso_utc(block_number, ts_cache),
                "tx_hash": log["transactionHash"],
                "log_index": str(int(log["logIndex"], 16)),
                "reserve_or_debt_asset": CRV,
                "collateral_asset": "",
                "user": user,
                "on_behalf_of_or_repayer": on_behalf_of,
                "liquidator": "",
                "amount_crv": decimal_units(amount_raw, 18),
                "collateral_amount_usdc": "",
                "borrow_rate_mode": str(int(decoded[2], 16)),
                "receive_a_token": "",
            }
        )

    # Repay is included as a negative check; no account CRV Repay logs were found in this window.
    repay_candidates = get_logs(event_start, event_end, [REPAY_TOPIC, padded_address(CRV)])
    repay_logs = receipt_logs_for_candidate_transactions(repay_candidates, REPAY_TOPIC)
    for log in repay_logs:
        if log["topics"][1].lower() != padded_address(CRV):
            continue
        user = address_from_word(log["topics"][2])
        repayer = address_from_word(log["topics"][3])
        if user.lower() != ACCOUNT.lower() and repayer.lower() != ACCOUNT.lower():
            continue
        block_number = int(log["blockNumber"], 16)
        amount_raw = int(words(log["data"])[0], 16)
        rows.append(
            {
                "event_type": "Repay",
                "block_number": str(block_number),
                "block_timestamp_utc": iso_utc(block_number, ts_cache),
                "tx_hash": log["transactionHash"],
                "log_index": str(int(log["logIndex"], 16)),
                "reserve_or_debt_asset": CRV,
                "collateral_asset": "",
                "user": user,
                "on_behalf_of_or_repayer": repayer,
                "liquidator": "",
                "amount_crv": decimal_units(amount_raw, 18),
                "collateral_amount_usdc": "",
                "borrow_rate_mode": "",
                "receive_a_token": "",
            }
        )

    liquidation_candidates = get_logs(
        event_start,
        event_end,
        [LIQUIDATION_TOPIC, None, padded_address(CRV), padded_address(ACCOUNT)],
    )
    liquidation_logs = receipt_logs_for_candidate_transactions(liquidation_candidates, LIQUIDATION_TOPIC)
    for log in liquidation_logs:
        if log["topics"][2].lower() != padded_address(CRV) or log["topics"][3].lower() != padded_address(ACCOUNT):
            continue
        decoded = words(log["data"])
        block_number = int(log["blockNumber"], 16)
        debt_raw = int(decoded[0], 16)
        collateral_raw = int(decoded[1], 16)
        rows.append(
            {
                "event_type": "LiquidationCall",
                "block_number": str(block_number),
                "block_timestamp_utc": iso_utc(block_number, ts_cache),
                "tx_hash": log["transactionHash"],
                "log_index": str(int(log["logIndex"], 16)),
                "reserve_or_debt_asset": CRV,
                "collateral_asset": address_from_word(log["topics"][1]),
                "user": ACCOUNT,
                "on_behalf_of_or_repayer": "",
                "liquidator": address_from_word(decoded[2]),
                "amount_crv": decimal_units(debt_raw, 18),
                "collateral_amount_usdc": decimal_units(collateral_raw, 6) if address_from_word(log["topics"][1]).lower() == USDC.lower() else "",
                "borrow_rate_mode": "",
                "receive_a_token": str(bool(int(decoded[3], 16))).lower(),
            }
        )

    rows.sort(key=lambda row: (int(row["block_number"]), int(row["log_index"])))
    csv_path = ROOT / "aave-v2-crv-account-events.csv"
    fieldnames = [
        "event_type",
        "block_number",
        "block_timestamp_utc",
        "tx_hash",
        "log_index",
        "reserve_or_debt_asset",
        "collateral_asset",
        "user",
        "on_behalf_of_or_repayer",
        "liquidator",
        "amount_crv",
        "collateral_amount_usdc",
        "borrow_rate_mode",
        "receive_a_token",
    ]
    with csv_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    borrow_rows = [row for row in rows if row["event_type"] == "Borrow"]
    repay_rows = [row for row in rows if row["event_type"] == "Repay"]
    liquidation_rows = [row for row in rows if row["event_type"] == "LiquidationCall"]

    def sum_crv(selected):
        return sum(Decimal(row["amount_crv"]) for row in selected)

    def sum_usdc_collateral(selected):
        return sum(Decimal(row["collateral_amount_usdc"]) for row in selected if row["collateral_amount_usdc"])

    summary = {
        "source": {
            "rpc_url": summary_rpc_url(),
            "methods": [
                "eth_getLogs for event discovery",
                "eth_getTransactionReceipt for canonical receipt logs",
                "eth_getBlockByNumber and eth_blockNumber for block/time discovery",
            ],
            "lending_pool": LENDING_POOL,
            "account": ACCOUNT,
            "crv": CRV,
            "usdc": USDC,
            "borrow_topic": BORROW_TOPIC,
            "repay_topic": REPAY_TOPIC,
            "liquidation_call_topic": LIQUIDATION_TOPIC,
        },
        "block_ranges": {
            "borrow_scan_from_2022_11_01_block": borrow_start,
            "event_scan_from_2022_11_21_block": event_start,
            "event_scan_to_2022_11_24_block": event_end,
        },
        "decoded_results": {
            "borrow_event_count": len(borrow_rows),
            "borrowed_crv_sum": f"{sum_crv(borrow_rows):.6f}",
            "repay_event_count_2022_11_21_to_24": len(repay_rows),
            "repaid_crv_sum_2022_11_21_to_24": f"{sum_crv(repay_rows):.6f}",
            "liquidation_call_count_2022_11_21_to_24": len(liquidation_rows),
            "liquidation_debt_covered_crv_sum": f"{sum_crv(liquidation_rows):.6f}",
            "liquidated_usdc_collateral_sum": f"{sum_usdc_collateral(liquidation_rows):.6f}",
            "first_liquidation_utc": liquidation_rows[0]["block_timestamp_utc"] if liquidation_rows else None,
            "last_liquidation_utc": liquidation_rows[-1]["block_timestamp_utc"] if liquidation_rows else None,
            "unique_liquidator_count": len({row["liquidator"].lower() for row in liquidation_rows}),
        },
        "notes": [
            "Borrow events are scanned from 2022-11-01 through 2022-11-24 to capture the account's staged CRV borrow buildup before the Nov 22 liquidation window.",
            "LiquidationCall events are filtered to debtAsset=CRV and user=0x57e04786e231af3343562c062e0d058f25dace9e from 2022-11-21 through 2022-11-24.",
            "Aave v2 CRV amounts use 18 token decimals; USDC collateral amounts use 6 decimals.",
        ],
    }
    (ROOT / "aave-v2-crv-onchain-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary["decoded_results"], indent=2))


if __name__ == "__main__":
    main()
