#!/usr/bin/env node

const fs = require("fs")
const path = require("path")

const RPC_URL = process.env.ETH_RPC_URL || "https://ethereum-rpc.publicnode.com"

const ATTACKER = "0x841ddf093f5188989fa1524e7b893de64b421f47"
const UWLEND_LENDING_POOL = "0x2409af0251dcb89ee3dee572629291f9b087c668"

const TXS = [
  {
    label: "attack-1",
    hash: "0x242a0fb4fde9de0dc2fd42e8db743cbc197ffa2bf6a036ba0bba303df296408b"
  },
  {
    label: "attack-2",
    hash: "0xb3f067618ce54bc26a960b660cfc28f9ea0315e2e9a1a855ede1508eb4017376"
  },
  {
    label: "attack-3",
    hash: "0xca1bbf3b320662c89232006f1ec6624b56242850f07e0f1dadbe4f69ba0d6ac3"
  }
]

const CONTROLLED_ADDRESSES = [
  ["attacker EOA", ATTACKER],
  ["exploit helper contract 1", "0x4fea76b66db8b548842349dc01c85278da3925da"],
  ["exploit helper contract 2", "0xf19d66e82ffe8e203b30df9e81359f8a201517ad"],
  ["exploit helper contract 3", "0x87ed9296bf492ee8807b80923205d8c1fd16f5d8"],
  ["exploit helper contract 4", "0x4cd6feba837b6944be0b2311b7a21036e86c3354"],
  ["crvUSD borrower contract", "0x6f8c5692b00c2ebbd07e4fd80e332dff3ab8e83c"]
]

const TOPICS = {
  transfer: "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
}

const SELECTORS = {
  symbol: "0x95d89b41",
  decimals: "0x313ce567"
}

const CHART_TOKEN_ORDER = [
  "WETH",
  "WBTC",
  "DAI",
  "USDC",
  "USDT",
  "FRAX",
  "GHO",
  "crvUSD",
  "CRV",
  "sDAI",
  "USDe",
  "sUSDe"
]

const tokenCache = new Map()
let requestId = 1

async function rpc(method, params) {
  let lastError
  for (let attempt = 0; attempt < 4; attempt += 1) {
    try {
      const response = await fetch(RPC_URL, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({
          jsonrpc: "2.0",
          id: requestId++,
          method,
          params
        })
      })
      const body = await response.json()
      if (body.error) {
        throw new Error(`${method}: ${JSON.stringify(body.error)}`)
      }
      return body.result
    } catch (error) {
      lastError = error
      await new Promise((resolve) => setTimeout(resolve, 250 * (attempt + 1)))
    }
  }
  throw lastError
}

async function ethCall(to, data) {
  try {
    const result = await rpc("eth_call", [{ to, data }, "latest"])
    return result && result !== "0x" ? result : null
  } catch {
    return null
  }
}

function hexToBigInt(hex) {
  return BigInt(hex || "0x0")
}

function hexToNumber(hex) {
  return Number(hexToBigInt(hex))
}

function topicAddress(topic) {
  return `0x${topic.slice(26).toLowerCase()}`
}

function cleanAscii(hex) {
  let out = ""
  for (let i = 0; i < hex.length; i += 2) {
    const code = parseInt(hex.slice(i, i + 2), 16)
    if (code >= 32 && code <= 126) out += String.fromCharCode(code)
  }
  return out.trim()
}

function decodeStringOrBytes32(hex) {
  if (!hex || hex === "0x") return null
  const data = hex.slice(2)

  try {
    if (data.length >= 128) {
      const offset = Number(BigInt(`0x${data.slice(0, 64)}`))
      const lengthStart = offset * 2
      const length = Number(
        BigInt(`0x${data.slice(lengthStart, lengthStart + 64)}`)
      )
      const value = cleanAscii(
        data.slice(lengthStart + 64, lengthStart + 64 + length * 2)
      )
      if (value) return value
    }
  } catch {
    // Fall through to bytes32 decoding.
  }

  return cleanAscii(data.slice(0, 64)) || null
}

async function tokenMeta(address) {
  const key = address.toLowerCase()
  if (tokenCache.has(key)) return tokenCache.get(key)

  const symbol = decodeStringOrBytes32(await ethCall(key, SELECTORS.symbol))
  const decimalsHex = await ethCall(key, SELECTORS.decimals)
  const decimals = decimalsHex ? Number(hexToBigInt(decimalsHex)) : 18
  const meta = {
    address: key,
    symbol: symbol || key.slice(0, 10),
    decimals
  }
  tokenCache.set(key, meta)
  return meta
}

function decimalString(value, decimals, digits = 6) {
  let amount = value
  const negative = amount < 0n
  if (negative) amount = -amount
  const scale = 10n ** BigInt(decimals)
  const whole = amount / scale
  const fractional = (amount % scale)
    .toString()
    .padStart(decimals, "0")
    .slice(0, digits)
    .replace(/0+$/g, "")
  return `${negative ? "-" : ""}${whole}${fractional ? `.${fractional}` : ""}`
}

function numberAmount(value, decimals) {
  return Number(value) / 10 ** decimals
}

function absBigInt(value) {
  return value < 0n ? -value : value
}

function isVisibleNet(value, decimals) {
  if (value === 0n) return false
  const threshold = 10n ** BigInt(Math.max(0, decimals - 6))
  return absBigInt(value) >= threshold
}

function tokenClass(symbol) {
  if (/debt/i.test(symbol)) return "debt-accounting"
  if (/^u[A-Z]/.test(symbol)) return "uwu-interest-token"
  return "liquid-token"
}

function csvEscape(value) {
  const text = String(value ?? "")
  return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text
}

function writeCsv(file, rows, columns) {
  const data = [
    columns.join(","),
    ...rows.map((row) =>
      columns.map((column) => csvEscape(row[column])).join(",")
    )
  ].join("\n")
  fs.writeFileSync(path.join(__dirname, file), `${data}\n`)
}

function svgFrame(width, height, body) {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img">
  <style>
    text { font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #17202a; }
    .muted { fill: #5d6d7e; font-size: 12px; }
    .title { font-size: 18px; font-weight: 700; }
    .axis { stroke: #d6dbdf; stroke-width: 1; }
    .bar { fill: #2f6f9f; }
    .bar-alt { fill: #1f7a5a; }
    .warn { fill: #9b2f2f; }
  </style>
${body}
</svg>
`
}

function writeTokenNetSvg(totalRows) {
  const rows = totalRows
    .filter((row) => row.token_class === "liquid-token" && row.net_raw > 0n)
    .sort((a, b) => {
      const orderA = CHART_TOKEN_ORDER.indexOf(a.symbol)
      const orderB = CHART_TOKEN_ORDER.indexOf(b.symbol)
      if (orderA !== -1 || orderB !== -1) {
        return (orderA === -1 ? 99 : orderA) - (orderB === -1 ? 99 : orderB)
      }
      return Math.abs(b.net_amount_number) - Math.abs(a.net_amount_number)
    })
    .slice(0, 12)

  const width = 940
  const rowHeight = 38
  const height = 90 + rows.length * rowHeight
  const left = 128
  const chartWidth = 660
  const max = Math.max(
    0,
    ...rows.map((row) => Math.log10(Math.abs(row.net_amount_number) + 1))
  )

  const bodyRows = rows
    .map((row, index) => {
      const y = 74 + index * rowHeight
      const magnitude = Math.log10(Math.abs(row.net_amount_number) + 1)
      const widthValue = max === 0 ? 0 : (magnitude / max) * chartWidth
      return `<text x="30" y="${y + 18}">${row.symbol}</text>
  <rect class="bar" x="${left}" y="${y}" width="${Math.max(
        2,
        widthValue
      )}" height="22" />
  <text class="muted" x="${left + Math.max(8, widthValue) + 10}" y="${
        y + 16
      }">${row.net_amount}</text>`
    })
    .join("\n")

  fs.writeFileSync(
    path.join(__dirname, "uwu-lend-token-net.svg"),
    svgFrame(
      width,
      height,
      `<text class="title" x="30" y="32">Net ERC-20 inflow to UwU Lend attacker-controlled addresses</text>
  <text class="muted" x="30" y="52">Liquid-token subset only; bars are log-scaled because token units are not directly comparable.</text>
  ${bodyRows}
  <text class="muted" x="30" y="${
    height - 20
  }">Source: Ethereum receipts for the three public UwU Lend attack transactions.</text>`
    )
  )
}

function writeReceiptLoadSvg(txSummaryRows) {
  const width = 940
  const height = 360
  const left = 90
  const top = 78
  const chartWidth = 760
  const chartHeight = 200
  const barWidth = 72
  const maxLogs = Math.max(...txSummaryRows.map((row) => row.log_count))
  const maxGas = Math.max(...txSummaryRows.map((row) => row.gas_used))

  const bars = txSummaryRows
    .map((row, index) => {
      const x = left + index * 240
      const logHeight = (row.log_count / maxLogs) * chartHeight
      const gasHeight = (row.gas_used / maxGas) * chartHeight
      return `<rect class="bar" x="${x}" y="${
        top + chartHeight - logHeight
      }" width="${barWidth}" height="${logHeight}" />
  <rect class="bar-alt" x="${x + 88}" y="${
        top + chartHeight - gasHeight
      }" width="${barWidth}" height="${gasHeight}" />
  <text x="${x}" y="${top + chartHeight + 28}">${row.tx_label}</text>
  <text class="muted" x="${x}" y="${top + chartHeight + 46}">block ${
        row.block_number
      }</text>
  <text class="muted" x="${x}" y="${top + chartHeight + 64}">${
        row.log_count
      } logs</text>`
    })
    .join("\n")

  fs.writeFileSync(
    path.join(__dirname, "uwu-lend-receipt-load.svg"),
    svgFrame(
      width,
      height,
      `<text class="title" x="30" y="34">Three executor-creation receipts from one attacker EOA</text>
  <text class="muted" x="30" y="55">Blue bars show receipt log count; green bars show gas used, normalized separately.</text>
  <line class="axis" x1="${left}" y1="${top + chartHeight}" x2="${
        left + chartWidth
      }" y2="${top + chartHeight}" />
  ${bars}
  <rect class="bar" x="706" y="30" width="14" height="14" />
  <text class="muted" x="728" y="42">logs</text>
  <rect class="bar-alt" x="776" y="30" width="14" height="14" />
  <text class="muted" x="798" y="42">gas used</text>`
    )
  )
}

function addAmount(map, key, patch) {
  if (!map.has(key)) {
    map.set(key, {
      incoming: 0n,
      outgoing: 0n,
      transfer_count: 0
    })
  }
  const row = map.get(key)
  row.incoming += patch.incoming || 0n
  row.outgoing += patch.outgoing || 0n
  row.transfer_count += patch.transfer_count || 0
}

async function main() {
  const controlledRows = CONTROLLED_ADDRESSES.map(([role, address]) => ({
    role,
    address: address.toLowerCase()
  }))
  const controlled = new Set(controlledRows.map((row) => row.address))
  const receipts = []

  for (const txInfo of TXS) {
    const [tx, receipt] = await Promise.all([
      rpc("eth_getTransactionByHash", [txInfo.hash]),
      rpc("eth_getTransactionReceipt", [txInfo.hash])
    ])
    const block = await rpc("eth_getBlockByNumber", [
      receipt.blockNumber,
      false
    ])
    const created = receipt.contractAddress
      ? receipt.contractAddress.toLowerCase()
      : ""
    if (created && !controlled.has(created)) {
      controlled.add(created)
      controlledRows.push({
        role: `${txInfo.label} created executor`,
        address: created
      })
    }
    receipts.push({
      txInfo,
      tx,
      receipt,
      block,
      created
    })
  }

  const perTxToken = new Map()
  const totalByToken = new Map()
  const txSummaryRows = []

  for (const item of receipts) {
    const receipt = item.receipt
    let transferLogs = 0
    const uniqueTokens = new Set()
    const txTokenCounts = new Map()

    for (const log of receipt.logs) {
      if (
        log.topics[0] !== TOPICS.transfer ||
        log.topics.length < 3 ||
        !log.data ||
        log.data === "0x"
      ) {
        continue
      }

      transferLogs += 1
      const from = topicAddress(log.topics[1])
      const to = topicAddress(log.topics[2])
      const fromControlled = controlled.has(from)
      const toControlled = controlled.has(to)
      if (fromControlled === toControlled) continue

      const value = hexToBigInt(log.data)
      const token = (await tokenMeta(log.address)).address
      uniqueTokens.add(token)
      const key = `${item.txInfo.hash}:${token}`
      const totalKey = token
      const patch = toControlled
        ? { incoming: value, transfer_count: 1 }
        : { outgoing: value, transfer_count: 1 }
      addAmount(perTxToken, key, patch)
      addAmount(totalByToken, totalKey, patch)
      txTokenCounts.set(token, true)
    }

    txSummaryRows.push({
      tx_label: item.txInfo.label,
      transaction_hash: item.txInfo.hash,
      from_address: item.tx.from.toLowerCase(),
      to_address: item.tx.to || "",
      created_contract: item.created,
      block_number: hexToNumber(receipt.blockNumber),
      timestamp_utc: new Date(hexToNumber(item.block.timestamp) * 1000)
        .toISOString()
        .replace(".000Z", "Z"),
      status: hexToNumber(receipt.status),
      gas_used: hexToNumber(receipt.gasUsed),
      log_count: receipt.logs.length,
      erc20_transfer_logs: transferLogs,
      controlled_flow_tokens: txTokenCounts.size
    })
  }

  const perTxRows = []
  for (const [key, value] of perTxToken.entries()) {
    const [txHash, tokenAddress] = key.split(":")
    const txInfo = TXS.find((tx) => tx.hash === txHash)
    const summary = txSummaryRows.find((row) => row.transaction_hash === txHash)
    const meta = await tokenMeta(tokenAddress)
    const net = value.incoming - value.outgoing
    if (!isVisibleNet(net, meta.decimals)) continue
    perTxRows.push({
      tx_label: txInfo.label,
      transaction_hash: txHash,
      block_number: summary.block_number,
      timestamp_utc: summary.timestamp_utc,
      created_contract: summary.created_contract,
      token_symbol: meta.symbol,
      token_class: tokenClass(meta.symbol),
      token_address: meta.address,
      incoming_amount: decimalString(value.incoming, meta.decimals),
      outgoing_amount: decimalString(value.outgoing, meta.decimals),
      net_amount: decimalString(net, meta.decimals),
      net_amount_number: numberAmount(net, meta.decimals),
      incoming_raw: value.incoming.toString(),
      outgoing_raw: value.outgoing.toString(),
      net_raw: net.toString(),
      transfer_count: value.transfer_count
    })
  }

  perTxRows.sort((a, b) => {
    if (a.block_number !== b.block_number)
      return a.block_number - b.block_number
    return Math.abs(b.net_amount_number) - Math.abs(a.net_amount_number)
  })

  const totalRows = []
  for (const [tokenAddress, value] of totalByToken.entries()) {
    const meta = await tokenMeta(tokenAddress)
    const net = value.incoming - value.outgoing
    if (!isVisibleNet(net, meta.decimals)) continue
    totalRows.push({
      symbol: meta.symbol,
      token_class: tokenClass(meta.symbol),
      token_address: meta.address,
      incoming_amount: decimalString(value.incoming, meta.decimals),
      outgoing_amount: decimalString(value.outgoing, meta.decimals),
      net_amount: decimalString(net, meta.decimals),
      net_amount_number: numberAmount(net, meta.decimals),
      incoming_raw: value.incoming.toString(),
      outgoing_raw: value.outgoing.toString(),
      net_raw: net,
      transfer_count: value.transfer_count
    })
  }

  totalRows.sort(
    (a, b) => Math.abs(b.net_amount_number) - Math.abs(a.net_amount_number)
  )

  const totalRowsForCsv = totalRows.map((row) => ({
    ...row,
    net_raw: row.net_raw.toString()
  }))

  writeCsv("uwu-lend-tx-summary.csv", txSummaryRows, [
    "tx_label",
    "transaction_hash",
    "from_address",
    "to_address",
    "created_contract",
    "block_number",
    "timestamp_utc",
    "status",
    "gas_used",
    "log_count",
    "erc20_transfer_logs",
    "controlled_flow_tokens"
  ])

  writeCsv("uwu-lend-controlled-addresses.csv", controlledRows, [
    "role",
    "address"
  ])

  writeCsv("uwu-lend-attack-transactions.csv", perTxRows, [
    "tx_label",
    "transaction_hash",
    "block_number",
    "timestamp_utc",
    "created_contract",
    "token_symbol",
    "token_class",
    "token_address",
    "incoming_amount",
    "outgoing_amount",
    "net_amount",
    "net_amount_number",
    "incoming_raw",
    "outgoing_raw",
    "net_raw",
    "transfer_count"
  ])

  writeCsv("uwu-lend-token-net.csv", totalRowsForCsv, [
    "symbol",
    "token_class",
    "token_address",
    "incoming_amount",
    "outgoing_amount",
    "net_amount",
    "net_amount_number",
    "incoming_raw",
    "outgoing_raw",
    "net_raw",
    "transfer_count"
  ])

  writeCsv(
    "uwu-lend-liquid-token-net.csv",
    totalRowsForCsv.filter((row) => row.token_class === "liquid-token"),
    [
      "symbol",
      "token_address",
      "incoming_amount",
      "outgoing_amount",
      "net_amount",
      "net_amount_number",
      "incoming_raw",
      "outgoing_raw",
      "net_raw",
      "transfer_count"
    ]
  )

  writeTokenNetSvg(totalRows)
  writeReceiptLoadSvg(txSummaryRows)

  console.log(
    `Wrote ${txSummaryRows.length} transaction rows and ${totalRows.length} token rows for ${UWLEND_LENDING_POOL}.`
  )
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
