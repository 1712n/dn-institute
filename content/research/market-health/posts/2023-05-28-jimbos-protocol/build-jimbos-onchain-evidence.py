from __future__ import annotations

import csv
import json
import math
from decimal import Decimal
from pathlib import Path
from urllib import request


RPC_URL = "https://arb1.arbitrum.io/rpc"
ATTACK_TX = "0x44a0f5650a038ab522087c02f734b80e6c748afb207995e757ed67ca037a5eda"
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
WETH = "0x82af49447d8a07e3bd95bd0d56f35241523fbab1"
WEI_PER_WETH = Decimal(10) ** 18

LABELS = {
    "0x0000000000000000000000000000000000000000": "zero_mint_burn",
    "0x102be4bccc2696c35fd5f5bfe54c1dfba416a741": "attacker_eoa",
    "0xd4002233b59f7edd726fc6f14303980841306973": "attack_contract",
    "0x271944d9d8ca831f7c0dbcb20c4ee482376d6de7": "jimbo_controller",
    "0x16a5d28b20a3fddecdcaf02df4b3935734df1a1f": "jimbo_weth_liquidity_book",
    "0xe50fa9b3c56ffb159cb0fca61f5c9d750e8128c8": "aave_arbitrum_weth",
    "0xb4315e873dbcf96ffd0acd8ea43f689d8c20fb30": "weth_pool_helper",
}

PLOT_ACTORS = [
    "attack_contract",
    "jimbo_controller",
    "jimbo_weth_liquidity_book",
]


def rpc(method: str, params: list[object]) -> dict:
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    req = request.Request(
        RPC_URL,
        payload,
        {"Content-Type": "application/json", "User-Agent": "dn-institute-jimbos-evidence/1.0"},
    )
    with request.urlopen(req, timeout=30) as response:
        data = json.loads(response.read().decode())
    if "error" in data:
        raise RuntimeError(data["error"])
    return data["result"]


def label(address: str) -> str:
    return LABELS.get(address.lower(), address.lower())


def topic_address(topic: str) -> str:
    return "0x" + topic[-40:].lower()


def weth_from_wei(amount_wei: int) -> Decimal:
    return Decimal(amount_wei) / WEI_PER_WETH


def format_decimal(value: Decimal, places: int | None = None) -> str:
    if places is not None:
        value = value.quantize(Decimal(1).scaleb(-places))
    if value == 0:
        value = Decimal(0)
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def fetch_weth_transfers() -> tuple[int, int, list[dict[str, object]]]:
    receipt = rpc("eth_getTransactionReceipt", [ATTACK_TX])
    rows = []
    for log in receipt["logs"]:
        topics = [topic.lower() for topic in log["topics"]]
        if log["address"].lower() != WETH or not topics or topics[0] != TRANSFER_TOPIC:
            continue

        amount_wei = int(log["data"], 16)
        from_address = topic_address(topics[1])
        to_address = topic_address(topics[2])
        rows.append(
            {
                "log_index": int(log["logIndex"], 16),
                "from_label": label(from_address),
                "to_label": label(to_address),
                "from_address": from_address,
                "to_address": to_address,
                "amount_wei": str(amount_wei),
                "amount_weth": format_decimal(weth_from_wei(amount_wei)),
            }
        )
    return int(receipt["blockNumber"], 16), len(receipt["logs"]), rows


def write_transfers(out_dir: Path, rows: list[dict[str, object]]) -> None:
    with (out_dir / "jimbos-exploit-weth-transfers.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "log_index",
                "from_label",
                "to_label",
                "from_address",
                "to_address",
                "amount_wei",
                "amount_weth",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def write_actor_summary(out_dir: Path, rows: list[dict[str, object]]) -> dict[str, dict[str, Decimal]]:
    balances: dict[str, Decimal] = {}
    stats: dict[str, dict[str, Decimal]] = {}

    def actor_stats(actor: str) -> dict[str, Decimal]:
        if actor not in stats:
            stats[actor] = {
                "gross_in_weth": Decimal(0),
                "gross_out_weth": Decimal(0),
                "net_delta_weth": Decimal(0),
                "max_positive_delta_weth": Decimal(0),
                "min_negative_delta_weth": Decimal(0),
            }
        return stats[actor]

    for row in rows:
        amount = weth_from_wei(int(row["amount_wei"]))
        sender = str(row["from_label"])
        receiver = str(row["to_label"])

        actor_stats(sender)["gross_out_weth"] += amount
        actor_stats(receiver)["gross_in_weth"] += amount

        balances[sender] = balances.get(sender, Decimal(0)) - amount
        balances[receiver] = balances.get(receiver, Decimal(0)) + amount

        for actor in (sender, receiver):
            current = balances[actor]
            actor_stats(actor)["net_delta_weth"] = current
            actor_stats(actor)["max_positive_delta_weth"] = max(
                actor_stats(actor)["max_positive_delta_weth"], current
            )
            actor_stats(actor)["min_negative_delta_weth"] = min(
                actor_stats(actor)["min_negative_delta_weth"], current
            )

    with (out_dir / "jimbos-exploit-weth-actors.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "actor",
                "gross_in_weth",
                "gross_out_weth",
                "net_delta_weth",
                "max_positive_delta_weth",
                "min_negative_delta_weth",
            ],
        )
        writer.writeheader()
        for actor in sorted(stats):
            writer.writerow({"actor": actor, **{k: format_decimal(v, 6) for k, v in stats[actor].items()}})
    return stats


def write_svg(out_dir: Path, rows: list[dict[str, object]]) -> None:
    width = 900
    height = 420
    left = 72
    right = 24
    top = 32
    bottom = 58
    plot_w = width - left - right
    plot_h = height - top - bottom

    balances = {actor: Decimal(0) for actor in PLOT_ACTORS}
    series = {actor: [(0, Decimal(0))] for actor in PLOT_ACTORS}
    max_log = max((int(row["log_index"]) for row in rows), default=0) or 1
    max_abs = Decimal(1)

    for row in rows:
        log_index = int(row["log_index"])
        amount = weth_from_wei(int(row["amount_wei"]))
        sender = str(row["from_label"])
        receiver = str(row["to_label"])
        if sender in balances:
            balances[sender] -= amount
        if receiver in balances:
            balances[receiver] += amount
        for actor in PLOT_ACTORS:
            series[actor].append((log_index, balances[actor]))
            max_abs = max(max_abs, abs(balances[actor]))

    y_limit = max(1, math.ceil(float(max_abs) / 1000) * 1000)

    def x_for(log_index: int) -> float:
        return left + (log_index / max_log) * plot_w

    def y_for(value: Decimal | int) -> float:
        return top + (float(Decimal(y_limit) - value) / (2 * y_limit)) * plot_h

    colors = {
        "attack_contract": "#f97316",
        "jimbo_controller": "#22c55e",
        "jimbo_weth_liquidity_book": "#38bdf8",
    }

    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="420" viewBox="0 0 900 420" role="img" aria-labelledby="title desc">',
        "<title id=\"title\">Jimbos exploit WETH transfer-implied balance deltas</title>",
        "<desc id=\"desc\">Line chart of WETH balance deltas for the attack contract, Jimbos controller, and liquidity book across exploit transaction log indexes.</desc>",
        '<rect width="900" height="420" fill="#111827"/>',
        f'<line x1="{left}" y1="{y_for(0):.2f}" x2="{width - right}" y2="{y_for(0):.2f}" stroke="#9ca3af" stroke-width="1"/>',
    ]

    for tick in range(-y_limit, y_limit + 1, max(1000, y_limit // 4)):
        y = y_for(tick)
        lines.append(f'<line x1="{left}" y1="{y:.2f}" x2="{width - right}" y2="{y:.2f}" stroke="#374151" stroke-width="0.75"/>')
        lines.append(f'<text x="{left - 10}" y="{y + 4:.2f}" fill="#d1d5db" font-size="12" text-anchor="end">{tick}</text>')

    for actor, points in series.items():
        path = " ".join(f"{x_for(x):.2f},{y_for(y):.2f}" for x, y in points)
        lines.append(f'<polyline fill="none" stroke="{colors[actor]}" stroke-width="2.5" points="{path}"/>')

    lines.extend(
        [
            f'<text x="{left}" y="24" fill="#f9fafb" font-size="16" font-weight="700">Exploit transaction WETH flow, transfer-implied deltas</text>',
            f'<text x="{left}" y="{height - 18}" fill="#d1d5db" font-size="12">x-axis: receipt log index; y-axis: WETH delta from transaction start</text>',
        ]
    )

    legend_x = 592
    for i, actor in enumerate(PLOT_ACTORS):
        y = 48 + i * 24
        lines.append(f'<rect x="{legend_x}" y="{y - 10}" width="12" height="12" fill="{colors[actor]}"/>')
        lines.append(f'<text x="{legend_x + 18}" y="{y}" fill="#f9fafb" font-size="13">{actor}</text>')

    lines.append("</svg>")
    (out_dir / "jimbos-exploit-weth-flow.svg").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    block_number, log_count, rows = fetch_weth_transfers()
    write_transfers(out_dir, rows)
    stats = write_actor_summary(out_dir, rows)
    write_svg(out_dir, rows)
    controller = stats.get("jimbo_controller", {})
    controller_gross_weth = controller.get("gross_in_weth", Decimal(0)) + controller.get(
        "gross_out_weth", Decimal(0)
    )
    print(f"block={block_number} receipt_logs={log_count} weth_transfers={len(rows)}")
    print(f"controller_gross_weth={format_decimal(controller_gross_weth, 6)}")


if __name__ == "__main__":
    main()
