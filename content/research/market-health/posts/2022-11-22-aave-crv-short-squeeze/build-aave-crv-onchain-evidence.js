const fs = require("fs")
const path = require("path")

const OUT_DIR = __dirname

const RPC_URLS = (
  process.env.ETH_RPC_URL ||
  "https://ethereum-rpc.publicnode.com,https://ethereum.publicnode.com,https://eth.drpc.org"
)
  .split(",")
  .map((url) => url.trim())
  .filter(Boolean)

const FROM_BLOCK = 15950000
const TO_BLOCK = 16030000
const LOG_STEP = 30000

const USER = "0x57e04786e231af3343562c062e0d058f25dace9e"
const AAVE_LENDING_POOL_V2 = "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9"
const CRV = "0xD533a949740bb3306d119CC777fa900bA034cd52"
const USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

const TOPICS = {
  transfer:
    "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
  deposit: "0xde6857219544bb5b7746f48ed30be6386fefc61b2f864cacf559893bf50fd951",
  borrow: "0xc6a898309e823ee50bac64e45ca8adba6690e99e7841c45d754e2a38e9019d9b",
  liquidation:
    "0xe413a321e8681d831f4dbccbca790d2952b56f977908e45be37335533e005286"
}

const TOKEN_DECIMALS = {
  CRV: 18,
  USDC: 6
}

const ZERO = "0x0000000000000000000000000000000000000000"

function padTopic(address) {
  return `0x${address.toLowerCase().replace(/^0x/, "").padStart(64, "0")}`
}

function hex(value) {
  return `0x${value.toString(16)}`
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

let rpcIndex = 0

async function rpc(method, params) {
  let lastError
  for (let attempt = 0; attempt < RPC_URLS.length * 3; attempt += 1) {
    const url = RPC_URLS[rpcIndex % RPC_URLS.length]
    rpcIndex += 1
    const controller = new AbortController()
    const timeout = setTimeout(() => controller.abort(), 20000)
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ jsonrpc: "2.0", id: 1, method, params }),
        signal: controller.signal
      })
      const text = await response.text()
      let body
      try {
        body = JSON.parse(text)
      } catch (error) {
        throw new Error(
          `non-JSON RPC response from ${url}: ${text.slice(0, 80)}`
        )
      }
      if (body.error) {
        throw new Error(`${url}: ${JSON.stringify(body.error)}`)
      }
      return body.result
    } catch (error) {
      lastError = error
      await sleep(250 * (attempt + 1))
    } finally {
      clearTimeout(timeout)
    }
  }
  throw lastError
}

async function getLogs(filter) {
  const logs = []
  for (let from = FROM_BLOCK; from <= TO_BLOCK; from += LOG_STEP) {
    const to = Math.min(TO_BLOCK, from + LOG_STEP - 1)
    const chunk = await rpc("eth_getLogs", [
      {
        ...filter,
        fromBlock: hex(from),
        toBlock: hex(to)
      }
    ])
    logs.push(...chunk)
  }
  return logs.sort(compareLogs)
}

function compareLogs(a, b) {
  return (
    Number.parseInt(a.blockNumber, 16) - Number.parseInt(b.blockNumber, 16) ||
    Number.parseInt(a.transactionIndex || "0x0", 16) -
      Number.parseInt(b.transactionIndex || "0x0", 16) ||
    Number.parseInt(a.logIndex || "0x0", 16) -
      Number.parseInt(b.logIndex || "0x0", 16)
  )
}

function words(data) {
  const raw = data.slice(2)
  const out = []
  for (let i = 0; i < raw.length; i += 64) {
    out.push(`0x${raw.slice(i, i + 64)}`)
  }
  return out
}

function topicToAddress(topic) {
  return `0x${topic.slice(-40)}`
}

function dataValue(data) {
  return BigInt(data)
}

function decimal(value, decimals, places = 6) {
  const negative = value < 0n
  let absolute = negative ? -value : value
  const base = 10n ** BigInt(decimals)
  const whole = absolute / base
  let fraction = (absolute % base).toString().padStart(decimals, "0")
  if (places !== null) {
    fraction = fraction.slice(0, places)
  }
  fraction = fraction.replace(/0+$/, "")
  return `${negative ? "-" : ""}${whole.toString()}${
    fraction ? `.${fraction}` : ""
  }`
}

function asNumber(value, decimals) {
  return Number(value) / 10 ** decimals
}

function csvEscape(value) {
  const text = String(value)
  return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text
}

function writeCsv(filename, columns, rows) {
  const lines = [columns.join(",")]
  for (const row of rows) {
    lines.push(columns.map((column) => csvEscape(row[column] ?? "")).join(","))
  }
  fs.writeFileSync(path.join(OUT_DIR, filename), `${lines.join("\n")}\n`)
}

const blockCache = new Map()
const receiptCache = new Map()

async function blockTimestamp(blockNumberHex) {
  const blockNumber = Number.parseInt(blockNumberHex, 16)
  if (!blockCache.has(blockNumber)) {
    const block = await rpc("eth_getBlockByNumber", [blockNumberHex, false])
    blockCache.set(blockNumber, Number.parseInt(block.timestamp, 16))
  }
  return blockCache.get(blockNumber)
}

async function transactionReceipt(txHash) {
  if (!receiptCache.has(txHash)) {
    receiptCache.set(txHash, await rpc("eth_getTransactionReceipt", [txHash]))
  }
  return receiptCache.get(txHash)
}

async function normalizedLogIndex(log) {
  const parsed = Number.parseInt(log.logIndex || "0x0", 16)
  if (parsed < 1_000_000) {
    return parsed
  }
  const receipt = await transactionReceipt(log.transactionHash)
  const match = receipt.logs.find(
    (candidate) =>
      candidate.address.toLowerCase() === log.address.toLowerCase() &&
      candidate.data.toLowerCase() === log.data.toLowerCase() &&
      candidate.topics.length === log.topics.length &&
      candidate.topics.every(
        (topic, index) =>
          topic.toLowerCase() === log.topics[index].toLowerCase()
      )
  )
  return match ? Number.parseInt(match.logIndex, 16) : parsed
}

async function enrichLog(log) {
  const timestamp = await blockTimestamp(log.blockNumber)
  return {
    block: Number.parseInt(log.blockNumber, 16),
    timestamp,
    datetime: new Date(timestamp * 1000).toISOString(),
    tx_hash: log.transactionHash,
    tx_index: Number.parseInt(log.transactionIndex || "0x0", 16),
    log_index: await normalizedLogIndex(log),
    log
  }
}

async function mapLogs(logs, mapper) {
  const rows = []
  for (const log of logs) {
    rows.push(mapper(await enrichLog(log)))
  }
  return rows.sort(
    (a, b) =>
      a.block - b.block || a.tx_index - b.tx_index || a.log_index - b.log_index
  )
}

function sumRaw(rows, column) {
  return rows.reduce((total, row) => total + BigInt(row[`${column}_raw`]), 0n)
}

function makeCumulativeRows(events, metricColumns) {
  const totals = Object.fromEntries(metricColumns.map((column) => [column, 0]))
  return events
    .sort((a, b) => a.timestamp - b.timestamp || a.block - b.block)
    .map((event) => {
      for (const column of metricColumns) {
        totals[column] += event[column] || 0
      }
      return {
        timestamp: event.timestamp,
        datetime: event.datetime,
        ...totals
      }
    })
}

function svgLineChart({
  filename,
  title,
  yLabel,
  series,
  rows,
  width = 920,
  height = 440
}) {
  const margin = { top: 44, right: 170, bottom: 62, left: 72 }
  const chartWidth = width - margin.left - margin.right
  const chartHeight = height - margin.top - margin.bottom
  const minX = Math.min(...rows.map((row) => row.timestamp))
  const maxX = Math.max(...rows.map((row) => row.timestamp))
  const maxY = Math.max(
    ...rows.flatMap((row) => series.map((item) => row[item.key] || 0)),
    1
  )
  const niceMaxY = Math.ceil((maxY * 1.05) / 5) * 5

  const x = (timestamp) =>
    margin.left + ((timestamp - minX) / (maxX - minX || 1)) * chartWidth
  const y = (value) =>
    margin.top + chartHeight - (value / niceMaxY) * chartHeight

  const yTicks = [0, 0.25, 0.5, 0.75, 1].map((fraction) => niceMaxY * fraction)
  const xTicks = [minX, minX + (maxX - minX) / 2, maxX]

  const polylines = series
    .map((item) => {
      const points = rows
        .map(
          (row) =>
            `${x(row.timestamp).toFixed(1)},${y(row[item.key] || 0).toFixed(1)}`
        )
        .join(" ")
      return `<polyline points="${points}" fill="none" stroke="${item.color}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" />`
    })
    .join("\n    ")

  const legend = series
    .map(
      (item, index) => `
    <g transform="translate(${width - margin.right + 28}, ${
        margin.top + 22 + index * 28
      })">
      <rect width="14" height="14" fill="${item.color}" rx="2" />
      <text x="22" y="12" font-size="13" fill="#24313d">${item.label}</text>
    </g>`
    )
    .join("")

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-label="${title}">
  <rect width="${width}" height="${height}" fill="#ffffff" />
  <text x="${
    margin.left
  }" y="26" font-family="Inter, Arial, sans-serif" font-size="20" font-weight="700" fill="#17202a">${title}</text>
  <g font-family="Inter, Arial, sans-serif" font-size="12" fill="#5d6d7e">
    ${yTicks
      .map(
        (tick) => `<g>
      <line x1="${margin.left}" x2="${margin.left + chartWidth}" y1="${y(
          tick
        ).toFixed(1)}" y2="${y(tick).toFixed(1)}" stroke="#d6dbdf" />
      <text x="${margin.left - 10}" y="${(y(tick) + 4).toFixed(
          1
        )}" text-anchor="end">${tick.toFixed(0)}</text>
    </g>`
      )
      .join("\n    ")}
    <line x1="${margin.left}" x2="${margin.left}" y1="${margin.top}" y2="${
    margin.top + chartHeight
  }" stroke="#9aa5ad" />
    <line x1="${margin.left}" x2="${margin.left + chartWidth}" y1="${
    margin.top + chartHeight
  }" y2="${margin.top + chartHeight}" stroke="#9aa5ad" />
    ${xTicks
      .map(
        (tick) =>
          `<text x="${x(tick).toFixed(1)}" y="${
            margin.top + chartHeight + 28
          }" text-anchor="middle">${new Date(tick * 1000)
            .toISOString()
            .slice(5, 16)
            .replace("T", " ")}</text>`
      )
      .join("\n    ")}
    <text x="${margin.left + chartWidth / 2}" y="${
    height - 16
  }" text-anchor="middle">UTC date and hour</text>
    <text transform="translate(18 ${
      margin.top + chartHeight / 2
    }) rotate(-90)" text-anchor="middle">${yLabel}</text>
  </g>
  <g>
    ${polylines}
  </g>
${legend}
</svg>
`
  fs.writeFileSync(path.join(OUT_DIR, filename), svg)
}

async function main() {
  const borrowLogs = await getLogs({
    address: AAVE_LENDING_POOL_V2,
    topics: [TOPICS.borrow, padTopic(CRV), padTopic(USER)]
  })
  const depositLogs = await getLogs({
    address: AAVE_LENDING_POOL_V2,
    topics: [TOPICS.deposit, padTopic(USDC), padTopic(USER)]
  })
  const liquidationLogs = await getLogs({
    address: AAVE_LENDING_POOL_V2,
    topics: [TOPICS.liquidation, padTopic(USDC), padTopic(CRV), padTopic(USER)]
  })
  const crvFromUserLogs = await getLogs({
    address: CRV,
    topics: [TOPICS.transfer, padTopic(USER)]
  })
  const crvToUserLogs = await getLogs({
    address: CRV,
    topics: [TOPICS.transfer, null, padTopic(USER)]
  })
  const usdcFromUserLogs = await getLogs({
    address: USDC,
    topics: [TOPICS.transfer, padTopic(USER)]
  })
  const usdcToUserLogs = await getLogs({
    address: USDC,
    topics: [TOPICS.transfer, null, padTopic(USER)]
  })

  const borrowRows = await mapLogs(borrowLogs, (entry) => {
    const data = words(entry.log.data)
    const amount = BigInt(data[1])
    return {
      datetime: entry.datetime,
      block: entry.block,
      tx_hash: entry.tx_hash,
      tx_index: entry.tx_index,
      log_index: entry.log_index,
      reserve: CRV,
      user: topicToAddress(entry.log.topics[2]),
      amount_crv: decimal(amount, TOKEN_DECIMALS.CRV, 6),
      amount_crv_raw: amount.toString()
    }
  })

  const depositRows = await mapLogs(depositLogs, (entry) => {
    const data = words(entry.log.data)
    const amount = BigInt(data[1])
    return {
      datetime: entry.datetime,
      block: entry.block,
      tx_hash: entry.tx_hash,
      tx_index: entry.tx_index,
      log_index: entry.log_index,
      reserve: USDC,
      user: topicToAddress(entry.log.topics[2]),
      amount_usdc: decimal(amount, TOKEN_DECIMALS.USDC, 6),
      amount_usdc_raw: amount.toString()
    }
  })

  const liquidationRows = await mapLogs(liquidationLogs, (entry) => {
    const data = words(entry.log.data)
    const debtToCover = BigInt(data[0])
    const liquidatedCollateral = BigInt(data[1])
    return {
      datetime: entry.datetime,
      block: entry.block,
      tx_hash: entry.tx_hash,
      tx_index: entry.tx_index,
      log_index: entry.log_index,
      collateral_asset: topicToAddress(entry.log.topics[1]),
      debt_asset: topicToAddress(entry.log.topics[2]),
      user: topicToAddress(entry.log.topics[3]),
      debt_to_cover_crv: decimal(debtToCover, TOKEN_DECIMALS.CRV, 6),
      debt_to_cover_crv_raw: debtToCover.toString(),
      liquidated_collateral_usdc: decimal(
        liquidatedCollateral,
        TOKEN_DECIMALS.USDC,
        6
      ),
      liquidated_collateral_usdc_raw: liquidatedCollateral.toString(),
      liquidator: topicToAddress(data[2] || ZERO),
      receive_atoken: BigInt(data[3] || "0x0") === 1n
    }
  })

  const transferRows = [
    ...(await mapLogs(crvFromUserLogs, (entry) => {
      const amount = dataValue(entry.log.data)
      return {
        datetime: entry.datetime,
        block: entry.block,
        tx_hash: entry.tx_hash,
        tx_index: entry.tx_index,
        log_index: entry.log_index,
        token: "CRV",
        direction: "from_user",
        counterparty: topicToAddress(entry.log.topics[2]),
        amount: decimal(amount, TOKEN_DECIMALS.CRV, 6),
        amount_raw: amount.toString()
      }
    })),
    ...(await mapLogs(crvToUserLogs, (entry) => {
      const amount = dataValue(entry.log.data)
      return {
        datetime: entry.datetime,
        block: entry.block,
        tx_hash: entry.tx_hash,
        tx_index: entry.tx_index,
        log_index: entry.log_index,
        token: "CRV",
        direction: "to_user",
        counterparty: topicToAddress(entry.log.topics[1]),
        amount: decimal(amount, TOKEN_DECIMALS.CRV, 6),
        amount_raw: amount.toString()
      }
    })),
    ...(await mapLogs(usdcFromUserLogs, (entry) => {
      const amount = dataValue(entry.log.data)
      return {
        datetime: entry.datetime,
        block: entry.block,
        tx_hash: entry.tx_hash,
        tx_index: entry.tx_index,
        log_index: entry.log_index,
        token: "USDC",
        direction: "from_user",
        counterparty: topicToAddress(entry.log.topics[2]),
        amount: decimal(amount, TOKEN_DECIMALS.USDC, 6),
        amount_raw: amount.toString()
      }
    })),
    ...(await mapLogs(usdcToUserLogs, (entry) => {
      const amount = dataValue(entry.log.data)
      return {
        datetime: entry.datetime,
        block: entry.block,
        tx_hash: entry.tx_hash,
        tx_index: entry.tx_index,
        log_index: entry.log_index,
        token: "USDC",
        direction: "to_user",
        counterparty: topicToAddress(entry.log.topics[1]),
        amount: decimal(amount, TOKEN_DECIMALS.USDC, 6),
        amount_raw: amount.toString()
      }
    }))
  ].sort(
    (a, b) =>
      a.block - b.block || a.tx_index - b.tx_index || a.log_index - b.log_index
  )

  const transfersByTx = new Map()
  for (const row of transferRows) {
    if (!transfersByTx.has(row.tx_hash)) {
      transfersByTx.set(row.tx_hash, {
        datetime: row.datetime,
        block: row.block,
        tx_hash: row.tx_hash,
        crv_out_raw: 0n,
        usdc_in_raw: 0n
      })
    }
    const group = transfersByTx.get(row.tx_hash)
    if (row.token === "CRV" && row.direction === "from_user") {
      group.crv_out_raw += BigInt(row.amount_raw)
    }
    if (row.token === "USDC" && row.direction === "to_user") {
      group.usdc_in_raw += BigInt(row.amount_raw)
    }
  }

  const saleRows = [...transfersByTx.values()]
    .filter((row) => row.crv_out_raw > 0n && row.usdc_in_raw > 0n)
    .sort((a, b) => a.block - b.block)
    .map((row) => {
      const crv = asNumber(row.crv_out_raw, TOKEN_DECIMALS.CRV)
      const usdc = asNumber(row.usdc_in_raw, TOKEN_DECIMALS.USDC)
      return {
        datetime: row.datetime,
        block: row.block,
        tx_hash: row.tx_hash,
        crv_out: decimal(row.crv_out_raw, TOKEN_DECIMALS.CRV, 6),
        crv_out_raw: row.crv_out_raw.toString(),
        usdc_in: decimal(row.usdc_in_raw, TOKEN_DECIMALS.USDC, 6),
        usdc_in_raw: row.usdc_in_raw.toString(),
        effective_usdc_per_crv: (usdc / crv).toFixed(6)
      }
    })

  const totalBorrowedCrv = sumRaw(borrowRows, "amount_crv")
  const totalDepositedUsdc = sumRaw(depositRows, "amount_usdc")
  const totalLiquidatedDebtCrv = sumRaw(liquidationRows, "debt_to_cover_crv")
  const totalLiquidatedCollateralUsdc = sumRaw(
    liquidationRows,
    "liquidated_collateral_usdc"
  )
  const totalCrvOut = transferRows
    .filter((row) => row.token === "CRV" && row.direction === "from_user")
    .reduce((sum, row) => sum + BigInt(row.amount_raw), 0n)
  const totalCrvIn = transferRows
    .filter((row) => row.token === "CRV" && row.direction === "to_user")
    .reduce((sum, row) => sum + BigInt(row.amount_raw), 0n)
  const totalUsdcOut = transferRows
    .filter((row) => row.token === "USDC" && row.direction === "from_user")
    .reduce((sum, row) => sum + BigInt(row.amount_raw), 0n)
  const totalUsdcIn = transferRows
    .filter((row) => row.token === "USDC" && row.direction === "to_user")
    .reduce((sum, row) => sum + BigInt(row.amount_raw), 0n)

  const summaryRows = [
    {
      metric: "Aave V2 CRV borrow events",
      value: borrowRows.length,
      unit: "events"
    },
    {
      metric: "CRV borrowed from Aave V2",
      value: decimal(totalBorrowedCrv, TOKEN_DECIMALS.CRV, 6),
      unit: "CRV"
    },
    {
      metric: "USDC deposited to Aave V2 by wallet",
      value: decimal(totalDepositedUsdc, TOKEN_DECIMALS.USDC, 6),
      unit: "USDC"
    },
    {
      metric: "CRV transfers from wallet",
      value: decimal(totalCrvOut, TOKEN_DECIMALS.CRV, 6),
      unit: "CRV"
    },
    {
      metric: "USDC transfers to wallet",
      value: decimal(totalUsdcIn, TOKEN_DECIMALS.USDC, 6),
      unit: "USDC"
    },
    {
      metric: "LiquidationCall events",
      value: liquidationRows.length,
      unit: "events"
    },
    {
      metric: "Liquidation debt covered",
      value: decimal(totalLiquidatedDebtCrv, TOKEN_DECIMALS.CRV, 6),
      unit: "CRV"
    },
    {
      metric: "USDC collateral liquidated",
      value: decimal(totalLiquidatedCollateralUsdc, TOKEN_DECIMALS.USDC, 6),
      unit: "USDC"
    },
    {
      metric: "Net wallet CRV transfer balance",
      value: decimal(totalCrvIn - totalCrvOut, TOKEN_DECIMALS.CRV, 6),
      unit: "CRV"
    },
    {
      metric: "Net wallet USDC transfer balance before aToken accounting",
      value: decimal(totalUsdcIn - totalUsdcOut, TOKEN_DECIMALS.USDC, 6),
      unit: "USDC"
    }
  ]

  writeCsv("aave-crv-borrows.csv", Object.keys(borrowRows[0]), borrowRows)
  writeCsv(
    "aave-crv-usdc-deposits.csv",
    Object.keys(depositRows[0]),
    depositRows
  )
  writeCsv(
    "aave-crv-liquidations.csv",
    Object.keys(liquidationRows[0]),
    liquidationRows
  )
  writeCsv(
    "aave-crv-wallet-transfers.csv",
    Object.keys(transferRows[0]),
    transferRows
  )
  writeCsv("aave-crv-sale-transfers.csv", Object.keys(saleRows[0]), saleRows)
  writeCsv("aave-crv-summary.csv", ["metric", "value", "unit"], summaryRows)

  const crvEvents = [
    ...borrowRows.map((row) => ({
      timestamp: Math.floor(new Date(row.datetime).getTime() / 1000),
      datetime: row.datetime,
      block: row.block,
      borrowed: Number(row.amount_crv) / 1_000_000,
      sentOut: 0,
      liquidated: 0
    })),
    ...transferRows
      .filter((row) => row.token === "CRV" && row.direction === "from_user")
      .map((row) => ({
        timestamp: Math.floor(new Date(row.datetime).getTime() / 1000),
        datetime: row.datetime,
        block: row.block,
        borrowed: 0,
        sentOut: Number(row.amount) / 1_000_000,
        liquidated: 0
      })),
    ...liquidationRows.map((row) => ({
      timestamp: Math.floor(new Date(row.datetime).getTime() / 1000),
      datetime: row.datetime,
      block: row.block,
      borrowed: 0,
      sentOut: 0,
      liquidated: Number(row.debt_to_cover_crv) / 1_000_000
    }))
  ]
  const crvCumulative = makeCumulativeRows(crvEvents, [
    "borrowed",
    "sentOut",
    "liquidated"
  ])
  svgLineChart({
    filename: "aave-crv-cumulative-crv-flow.svg",
    title: "CRV borrowed, transferred out, and liquidated",
    yLabel: "Cumulative CRV, millions",
    rows: crvCumulative,
    series: [
      { key: "borrowed", label: "Borrowed", color: "#145a96" },
      { key: "sentOut", label: "Transferred out", color: "#9a5a00" },
      { key: "liquidated", label: "Liquidated debt", color: "#9b2f2f" }
    ]
  })

  const usdcEvents = [
    ...transferRows
      .filter((row) => row.token === "USDC" && row.direction === "to_user")
      .map((row) => ({
        timestamp: Math.floor(new Date(row.datetime).getTime() / 1000),
        datetime: row.datetime,
        block: row.block,
        received: Number(row.amount) / 1_000_000,
        deposited: 0,
        liquidated: 0
      })),
    ...depositRows.map((row) => ({
      timestamp: Math.floor(new Date(row.datetime).getTime() / 1000),
      datetime: row.datetime,
      block: row.block,
      received: 0,
      deposited: Number(row.amount_usdc) / 1_000_000,
      liquidated: 0
    })),
    ...liquidationRows.map((row) => ({
      timestamp: Math.floor(new Date(row.datetime).getTime() / 1000),
      datetime: row.datetime,
      block: row.block,
      received: 0,
      deposited: 0,
      liquidated: Number(row.liquidated_collateral_usdc) / 1_000_000
    }))
  ]
  const usdcCumulative = makeCumulativeRows(usdcEvents, [
    "received",
    "deposited",
    "liquidated"
  ])
  svgLineChart({
    filename: "aave-crv-cumulative-usdc-flow.svg",
    title: "USDC proceeds, collateral deposits, and liquidation",
    yLabel: "Cumulative USDC, millions",
    rows: usdcCumulative,
    series: [
      { key: "received", label: "Received by wallet", color: "#1f7a5a" },
      { key: "deposited", label: "Deposited to Aave", color: "#145a96" },
      { key: "liquidated", label: "Collateral liquidated", color: "#9b2f2f" }
    ]
  })

  console.log(
    `Wrote ${borrowRows.length} borrow rows, ${saleRows.length} sale rows, and ${liquidationRows.length} liquidation rows.`
  )
}

main().catch((error) => {
  console.error(error)
  process.exitCode = 1
})
