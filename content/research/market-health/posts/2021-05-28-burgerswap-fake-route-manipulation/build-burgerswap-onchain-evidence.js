#!/usr/bin/env node

const fs = require("fs")
const path = require("path")

const RPC_URL = process.env.BSC_RPC_URL || "https://bsc-dataseed.binance.org/"
const ATTACK_CONTRACT = "0xae0f538409063e66ff0e382113cb1a051fc069cd"
const ATTACK_WALLET = "0x6c9f2b95ca3432e5ec5bcd9c19de0636a23a4994"
const BURGER_WBNB_PAIR = "0x7ac55ac530f2c29659573bde0700c6758d69e677"

const TXS = [
  "0xac8a739c1f668b13d065d56a03c37a686e0aa1c9339e79fcbc5a2d0a6311e333",
  "0x40aef37b32748b1eb0e6eff69e2cdb1dbe8f169c8248bf20bf6c29998c1a07da",
  "0x943cd050af7f9f61243ada4e327b6606bf49ac01d92c86f70f0a6ec7bc2044da",
  "0x7ba354214b25cedd9ed18c034b8a110c1f04dadcb0aab1ea8be363eaf6d03eb9",
  "0x655eab143487a82a540ca122a9fcf7536cca58962c4212307915f83937c3be33",
  "0xde04b4785c3c157b0d7efd717d91828176b885da44317092bf69ccd1f631164d",
  "0xcf51d68653d9776dfc40e0db3aba2a6f1c63bf48a4266bd94280235e63d7c9dc",
  "0x4bdfcac1a0a8e836aaa00d165dc0d1873761bd46a574c3d09838d40333eb0e34",
  "0x28393240efab07f62f0ec3ac96060eae2e6bfd41ad37224d902b3ac6923be5c9",
  "0xb63a3576ef18e483bb0135f999d1fd54a5530bbf27023a54c61dbd877de328de",
  "0x0c24adf9e10ba7e133efd5544f1a3a4f93476898e266e1c7b2f393467bdacd40",
  "0x333ce235762dbc1089cbcdcc8590f22b38c888ed2c2cb9dd1263afcb5f679c3d",
  "0x2e1c226db4e8df3e08810ee96c35af355f1360487b180f726615b6191969beac"
]

const TOPICS = {
  transfer:
    "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
  swap: "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822",
  sync: "0x1c411e9a96e071241c2f21f7726b17ae89e3cab4c78be50e062b03a9fffbbad1"
}

const SELECTORS = {
  symbol: "0x95d89b41",
  decimals: "0x313ce567",
  token0: "0x0dfe1681",
  token1: "0xd21220a7"
}

const TOKEN_COLUMNS = [
  "WBNB",
  "BURGER",
  "USDT",
  "xBURGER",
  "BUSD",
  "ETH",
  "ROCKI"
]

const tokenCache = new Map()
const pairCache = new Map()

async function rpc(method, params) {
  const response = await fetch(RPC_URL, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ jsonrpc: "2.0", id: 1, method, params })
  })
  const body = await response.json()
  if (body.error) {
    throw new Error(`${method}: ${JSON.stringify(body.error)}`)
  }
  return body.result
}

async function ethCall(to, data) {
  try {
    const result = await rpc("eth_call", [{ to, data }, "latest"])
    return result && result !== "0x" ? result : null
  } catch {
    return null
  }
}

function words(data) {
  const clean = data.slice(2)
  const result = []
  for (let i = 0; i < clean.length; i += 64) {
    result.push(BigInt(`0x${clean.slice(i, i + 64)}`))
  }
  return result
}

function topicAddress(topic) {
  return `0x${topic.slice(26).toLowerCase()}`
}

function hexToAscii(hex) {
  let out = ""
  for (let i = 2; i < hex.length; i += 2) {
    const code = parseInt(hex.slice(i, i + 2), 16)
    if (code) out += String.fromCharCode(code)
  }
  return out.replace(/[\u0000-\u001f]+/g, "").trim()
}

async function tokenMeta(address) {
  const key = address.toLowerCase()
  if (tokenCache.has(key)) return tokenCache.get(key)

  let symbol = key.slice(0, 8)
  const symbolHex = await ethCall(key, SELECTORS.symbol)
  if (symbolHex) {
    try {
      const decoded = words(symbolHex)
      if (decoded.length >= 2) {
        const len = Number(decoded[1])
        const value = hexToAscii(`0x${symbolHex.slice(130, 130 + len * 2)}`)
        if (value) symbol = value
      } else {
        symbol = hexToAscii(symbolHex) || symbol
      }
    } catch {
      symbol = hexToAscii(symbolHex) || symbol
    }
  }
  if (key === "0xa61275f7fbd1959d2a1c9a298e602929f412d2e1") {
    symbol = "FAKE"
  }

  let decimals = 18
  const decimalsHex = await ethCall(key, SELECTORS.decimals)
  if (decimalsHex) decimals = Number(BigInt(decimalsHex))

  const meta = { address: key, symbol, decimals }
  tokenCache.set(key, meta)
  return meta
}

async function pairTokens(address) {
  const key = address.toLowerCase()
  if (pairCache.has(key)) return pairCache.get(key)

  const callAddress = async (selector) => {
    const value = await ethCall(key, selector)
    return value ? `0x${value.slice(-40).toLowerCase()}` : null
  }
  const pair = {
    token0: await callAddress(SELECTORS.token0),
    token1: await callAddress(SELECTORS.token1)
  }
  pairCache.set(key, pair)
  return pair
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
    .line { fill: none; stroke: #1f7a5a; stroke-width: 3; }
    .point { fill: #1f7a5a; }
    .bar { fill: #2f6f9f; }
    .warn { fill: #9b2f2f; }
  </style>
${body}
</svg>
`
}

function writeReservePriceSvg(syncRows) {
  const width = 920
  const height = 420
  const left = 72
  const top = 56
  const chartWidth = 790
  const chartHeight = 270
  if (syncRows.length === 0) {
    fs.writeFileSync(
      path.join(__dirname, "burgerswap-reserve-price.svg"),
      svgFrame(
        width,
        height,
        `<text class="title" x="32" y="32">BURGER/WBNB reserve-implied price inside the first attack transaction</text>
  <text class="muted" x="32" y="52">No Sync logs were found in the fetched receipt.</text>`
      )
    )
    return
  }
  const maxPrice = Math.max(
    ...syncRows.map((row) => row.reserve_price_wbnb_per_burger)
  )
  const minPrice = Math.min(
    ...syncRows.map((row) => row.reserve_price_wbnb_per_burger)
  )
  const xDenominator = Math.max(1, syncRows.length - 1)
  const priceRange = maxPrice - minPrice
  const x = (i) => left + (i * chartWidth) / xDenominator
  const y = (price) =>
    priceRange === 0
      ? top + chartHeight / 2
      : top + chartHeight - ((price - minPrice) / priceRange) * chartHeight
  const points = syncRows
    .map((row, i) => `${x(i)},${y(row.reserve_price_wbnb_per_burger)}`)
    .join(" ")
  const labels = syncRows
    .map((row, i) => {
      const px = x(i)
      const py = y(row.reserve_price_wbnb_per_burger)
      return `<circle class="point" cx="${px}" cy="${py}" r="4" />
  <text class="muted" x="${px - 16}" y="${top + chartHeight + 28}">${
        row.log_index
      }</text>`
    })
    .join("\n")

  fs.writeFileSync(
    path.join(__dirname, "burgerswap-reserve-price.svg"),
    svgFrame(
      width,
      height,
      `<text class="title" x="32" y="32">BURGER/WBNB reserve-implied price inside the first attack transaction</text>
  <text class="muted" x="32" y="52">Price is WBNB reserve divided by BURGER reserve at each Sync log; x-axis labels are receipt log indexes.</text>
  <line class="axis" x1="${left}" y1="${top}" x2="${left}" y2="${
        top + chartHeight
      }" />
  <line class="axis" x1="${left}" y1="${top + chartHeight}" x2="${
        left + chartWidth
      }" y2="${top + chartHeight}" />
  <text class="muted" x="18" y="${top + 5}">${maxPrice.toFixed(3)}</text>
  <text class="muted" x="20" y="${top + chartHeight}">${minPrice.toFixed(
        3
      )}</text>
  <polyline class="line" points="${points}" />
  ${labels}
  <text class="muted" x="${left}" y="${
        height - 28
      }">Source: BNB Smart Chain receipt 0xac8a739c...</text>`
    )
  )
}

function writeTokenTakeSvg(totalRows) {
  const rows = totalRows.filter((row) => TOKEN_COLUMNS.includes(row.symbol))
  const width = 920
  const rowHeight = 38
  const height = 90 + rows.length * rowHeight
  const left = 132
  const max = Math.max(
    0,
    ...rows.map((row) => Math.log10(Math.abs(row.amount_number) + 1))
  )
  const bodyRows = rows
    .map((row, index) => {
      const y = 76 + index * rowHeight
      const size = Math.log10(Math.abs(row.amount_number) + 1)
      const barWidth = max === 0 ? 0 : (size / max) * 620
      return `<text x="32" y="${y + 17}">${row.symbol}</text>
  <rect class="bar" x="${left}" y="${y}" width="${barWidth}" height="24" rx="3" />
  <text class="muted" x="${left + barWidth + 10}" y="${y + 17}">${
        row.net_amount
      }</text>`
    })
    .join("\n")

  fs.writeFileSync(
    path.join(__dirname, "burgerswap-token-net.svg"),
    svgFrame(
      width,
      height,
      `<text class="title" x="32" y="32">Net token inflow to the BurgerSwap attacker contract and wallet</text>
  <text class="muted" x="32" y="52">Log-scaled bars keep unlike token units readable; exact unit amounts are printed next to each bar.</text>
  ${bodyRows}`
    )
  )
}

async function main() {
  const transactionRows = []
  const totalByToken = new Map()
  const firstSwapRows = []
  const firstSyncRows = []

  for (const txHash of TXS) {
    const [tx, receipt] = await Promise.all([
      rpc("eth_getTransactionByHash", [txHash]),
      rpc("eth_getTransactionReceipt", [txHash])
    ])
    const txNetByToken = new Map()

    for (const log of receipt.logs) {
      const topic = log.topics[0]?.toLowerCase()
      const logAddress = log.address.toLowerCase()

      if (topic === TOPICS.transfer) {
        const token = await tokenMeta(logAddress)
        const from = topicAddress(log.topics[1])
        const to = topicAddress(log.topics[2])
        const amount = words(log.data)[0]
        for (const account of [ATTACK_CONTRACT, ATTACK_WALLET]) {
          if (to === account) {
            txNetByToken.set(
              logAddress,
              (txNetByToken.get(logAddress) || 0n) + amount
            )
            totalByToken.set(
              logAddress,
              (totalByToken.get(logAddress) || 0n) + amount
            )
          }
          if (from === account) {
            txNetByToken.set(
              logAddress,
              (txNetByToken.get(logAddress) || 0n) - amount
            )
            totalByToken.set(
              logAddress,
              (totalByToken.get(logAddress) || 0n) - amount
            )
          }
        }
      }

      if (txHash === TXS[0] && topic === TOPICS.swap) {
        const pair = await pairTokens(logAddress)
        const token0 = await tokenMeta(pair.token0)
        const token1 = await tokenMeta(pair.token1)
        const [amount0In, amount1In, amount0Out, amount1Out] = words(log.data)
        const amount0 = amount0In > 0n ? amount0In : amount0Out
        const amount1 = amount1In > 0n ? amount1In : amount1Out
        const isBurgerWbnb = logAddress === BURGER_WBNB_PAIR
        const burgerAmount =
          token0.symbol === "BURGER"
            ? numberAmount(amount0, token0.decimals)
            : null
        const wbnbAmount =
          token1.symbol === "WBNB"
            ? numberAmount(amount1, token1.decimals)
            : null
        firstSwapRows.push({
          log_index: Number(BigInt(log.logIndex)),
          pair: logAddress,
          token0: token0.symbol,
          token1: token1.symbol,
          amount0_in: decimalString(amount0In, token0.decimals),
          amount1_in: decimalString(amount1In, token1.decimals),
          amount0_out: decimalString(amount0Out, token0.decimals),
          amount1_out: decimalString(amount1Out, token1.decimals),
          effective_wbnb_per_burger:
            isBurgerWbnb && burgerAmount && wbnbAmount
              ? (wbnbAmount / burgerAmount).toFixed(9)
              : ""
        })
      }

      if (
        txHash === TXS[0] &&
        logAddress === BURGER_WBNB_PAIR &&
        topic === TOPICS.sync
      ) {
        const [reserveBurgerRaw, reserveWbnbRaw] = words(log.data)
        const reserveBurger = numberAmount(reserveBurgerRaw, 18)
        const reserveWbnb = numberAmount(reserveWbnbRaw, 18)
        firstSyncRows.push({
          log_index: Number(BigInt(log.logIndex)),
          reserve_burger: reserveBurger.toFixed(6),
          reserve_wbnb: reserveWbnb.toFixed(6),
          reserve_price_wbnb_per_burger: reserveWbnb / reserveBurger
        })
      }
    }

    const row = {
      tx_hash: txHash,
      block_number: Number(BigInt(tx.blockNumber)),
      tx_index: Number(BigInt(tx.transactionIndex)),
      log_count: receipt.logs.length
    }
    for (const symbol of TOKEN_COLUMNS) row[`net_${symbol.toLowerCase()}`] = "0"
    for (const [tokenAddress, amount] of txNetByToken.entries()) {
      const meta = await tokenMeta(tokenAddress)
      if (TOKEN_COLUMNS.includes(meta.symbol)) {
        row[`net_${meta.symbol.toLowerCase()}`] = decimalString(
          amount,
          meta.decimals
        )
      }
    }
    transactionRows.push(row)
  }

  const totalRows = []
  for (const [tokenAddress, amount] of totalByToken.entries()) {
    const meta = await tokenMeta(tokenAddress)
    if (!TOKEN_COLUMNS.includes(meta.symbol)) continue
    totalRows.push({
      symbol: meta.symbol,
      token_address: tokenAddress,
      decimals: meta.decimals,
      net_amount: decimalString(amount, meta.decimals),
      raw_amount: amount.toString(),
      amount_number: numberAmount(amount, meta.decimals)
    })
  }
  totalRows.sort(
    (a, b) => Math.abs(b.amount_number) - Math.abs(a.amount_number)
  )
  transactionRows.sort(
    (a, b) => a.block_number - b.block_number || a.tx_index - b.tx_index
  )
  firstSyncRows.sort((a, b) => a.log_index - b.log_index)
  firstSwapRows.sort((a, b) => a.log_index - b.log_index)

  writeCsv("burgerswap-attack-token-net.csv", totalRows, [
    "symbol",
    "token_address",
    "decimals",
    "net_amount",
    "raw_amount"
  ])
  writeCsv("burgerswap-attack-transactions.csv", transactionRows, [
    "tx_hash",
    "block_number",
    "tx_index",
    "log_count",
    ...TOKEN_COLUMNS.map((symbol) => `net_${symbol.toLowerCase()}`)
  ])
  writeCsv("burgerswap-first-transaction-swaps.csv", firstSwapRows, [
    "log_index",
    "pair",
    "token0",
    "token1",
    "amount0_in",
    "amount1_in",
    "amount0_out",
    "amount1_out",
    "effective_wbnb_per_burger"
  ])
  writeCsv(
    "burgerswap-first-transaction-sync.csv",
    firstSyncRows.map((row) => ({
      ...row,
      reserve_price_wbnb_per_burger:
        row.reserve_price_wbnb_per_burger.toFixed(9)
    })),
    [
      "log_index",
      "reserve_burger",
      "reserve_wbnb",
      "reserve_price_wbnb_per_burger"
    ]
  )
  writeReservePriceSvg(firstSyncRows)
  writeTokenTakeSvg(totalRows)

  console.log(
    `Wrote ${transactionRows.length} transaction rows and ${totalRows.length} token rows.`
  )
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
