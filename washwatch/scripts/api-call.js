// WashWatch - Market Manipulation Intelligence Data Fetcher
// Fetches crypto market manipulation signals from CPW API
// and enriches them with market health context

import { writeFile, readFile, mkdir } from "fs/promises"

const API_URL = "https://cpw-tracker.p.rapidapi.com/"
const API_KEY = process.env.RAPIDAPI_KEY

if (!API_KEY) {
  console.error("Error: RAPIDAPI_KEY environment variable is required")
  process.exit(1)
}

/**
 * Get date range for data collection
 * Fetches the last 7 days of market manipulation signals
 * @returns {Object} startTime and endTime ISO strings
 */
function getDateRange() {
  const now = new Date()
  const endTime = now
  const startTime = new Date(now)
  startTime.setDate(startTime.getDate() - 7) // Last 7 days for comprehensive coverage
  return {
    startTime: startTime.toISOString(),
    endTime: endTime.toISOString(),
  }
}

/**
 * Fetch wash trading and market manipulation signals
 * Monitors crypto exchanges for manipulation patterns
 * @returns {Promise<Array>} Array of manipulation event objects
 */
async function fetchManipulationSignals() {
  const { startTime, endTime } = getDateRange()

  console.log(`[WashWatch] Scanning for manipulation signals: ${startTime} to ${endTime}`)

  // Query 1: Wash trading signals at crypto exchanges
  const washTradingResponse = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-rapidapi-host": "cpw-tracker.p.rapidapi.com",
      "x-rapidapi-key": API_KEY,
    },
    body: JSON.stringify({
      entities: "cryptocurrency exchanges",
      topic: "wash trading",
      startTime,
      endTime,
    }),
  })

  // Query 2: Market manipulation signals
  const manipulationResponse = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-rapidapi-host": "cpw-tracker.p.rapidapi.com",
      "x-rapidapi-key": API_KEY,
    },
    body: JSON.stringify({
      entities: "cryptocurrency exchanges",
      topic: "market manipulation",
      startTime,
      endTime,
    }),
  })

  // Query 3: Spoofing and layering
  const spoofingResponse = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-rapidapi-host": "cpw-tracker.p.rapidapi.com",
      "x-rapidapi-key": API_KEY,
    },
    body: JSON.stringify({
      entities: "cryptocurrency trading",
      topic: "spoofing layering fraud",
      startTime,
      endTime,
    }),
  })

  // Query 4: Pump and dump schemes
  const pumpDumpResponse = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-rapidapi-host": "cpw-tracker.p.rapidapi.com",
      "x-rapidapi-key": API_KEY,
    },
    body: JSON.stringify({
      entities: "cryptocurrency tokens",
      topic: "pump and dump scheme",
      startTime,
      endTime,
    }),
  })

  const washData = washTradingResponse.ok
    ? await washTradingResponse.json()
    : []
  const manipData = manipulationResponse.ok
    ? await manipulationResponse.json()
    : []
  const spoofData = spoofingResponse.ok
    ? await spoofingResponse.json()
    : []
  const pumpData = pumpDumpResponse.ok
    ? await pumpDumpResponse.json()
    : []

  // Tag each signal with its category
  const tagSignals = (signals, category) =>
    (Array.isArray(signals) ? signals : []).map((s) => ({
      ...s,
      category,
    }))

  const allSignals = [
    ...tagSignals(washData, "wash-trading"),
    ...tagSignals(manipData, "market-manipulation"),
    ...tagSignals(spoofData, "spoofing-layering"),
    ...tagSignals(pumpData, "pump-and-dump"),
  ]

  console.log(
    `[WashWatch] Found ${allSignals.length} signals (wash: ${washData.length || 0}, manipulation: ${manipData.length || 0}, spoofing: ${spoofData.length || 0}, pump-dump: ${pumpData.length || 0})`
  )

  return allSignals
}

/**
 * Classify signal severity based on content analysis
 * @param {Object} signal - The signal object
 * @returns {string} Severity level: critical, high, medium, low
 */
function classifySeverity(signal) {
  const text = (signal.eventSummary || "").toLowerCase()

  if (
    text.includes("billion") ||
    text.includes("massive") ||
    text.includes("systemic") ||
    text.includes("collapse") ||
    text.includes("investigation") ||
    text.includes("sec ") ||
    text.includes("cftc") ||
    text.includes("doj ")
  ) {
    return "critical"
  }
  if (
    text.includes("million") ||
    text.includes("significant") ||
    text.includes("major") ||
    text.includes("lawsuit") ||
    text.includes("penalty") ||
    text.includes("fine")
  ) {
    return "high"
  }
  if (
    text.includes("suspicious") ||
    text.includes("unusual") ||
    text.includes("anomal") ||
    text.includes("warning")
  ) {
    return "medium"
  }
  return "low"
}

/**
 * Extract affected entities from signal text
 * @param {Object} signal - The signal object
 * @returns {Array<string>} List of entity names
 */
function extractEntities(signal) {
  const entities = []
  if (signal.entities) {
    entities.push(signal.entities)
  }

  // Extract exchange names from summary
  const exchangePatterns = [
    "Binance", "Coinbase", "OKX", "Bybit", "Huobi", "HTX", "KuCoin",
    "Kraken", "Bitfinex", "Gate.io", "Gemini", "Upbit", "Bithumb",
    "Bitstamp", "Crypto.com", "dYdX", "Uniswap", "Jupiter", "Raydium",
    "Polymarket", "FTX", "BitMEX",
  ]

  const text = signal.eventSummary || ""
  for (const exchange of exchangePatterns) {
    if (text.includes(exchange)) {
      entities.push(exchange)
    }
  }

  return [...new Set(entities)]
}

/**
 * Process and enrich signals with metadata
 * @param {Array} signals - Raw signal array
 * @returns {Array} Enriched signal array
 */
function enrichSignals(signals) {
  return signals.map((signal) => ({
    ...signal,
    severity: classifySeverity(signal),
    affectedEntities: extractEntities(signal),
    detectedAt: new Date().toISOString(),
  }))
}

/**
 * Save signals to data file, merging with existing data
 * Keeps a rolling window of the last 90 days
 * @param {Array} newSignals - New signals to add
 */
async function saveSignals(newSignals) {
  let existingSignals = []

  try {
    const existing = await readFile("data/signals.json", "utf-8")
    existingSignals = JSON.parse(existing)
  } catch {
    // No existing file, start fresh
  }

  // Merge and deduplicate by timestamp + entities combo
  const signalMap = new Map()

  for (const signal of existingSignals) {
    const key = `${signal.timestamp}-${signal.entities}-${signal.category}`
    signalMap.set(key, signal)
  }

  for (const signal of newSignals) {
    const key = `${signal.timestamp}-${signal.entities}-${signal.category}`
    signalMap.set(key, signal)
  }

  // Sort by timestamp descending
  const merged = [...signalMap.values()].sort(
    (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
  )

  // Keep last 90 days
  const cutoff = new Date()
  cutoff.setDate(cutoff.getDate() - 90)
  const filtered = merged.filter((s) => new Date(s.timestamp) >= cutoff)

  await mkdir("data", { recursive: true })
  await writeFile("data/signals.json", JSON.stringify(filtered, null, 2))

  // Generate stats summary
  const stats = generateStats(filtered)
  await writeFile("data/stats.json", JSON.stringify(stats, null, 2))

  console.log(
    `[WashWatch] Saved ${filtered.length} signals (${newSignals.length} new, ${existingSignals.length} existing)`
  )
}

/**
 * Generate aggregate statistics from signals
 * @param {Array} signals - All signals
 * @returns {Object} Statistics object
 */
function generateStats(signals) {
  const now = new Date()
  const last7Days = signals.filter(
    (s) => new Date(s.timestamp) >= new Date(now - 7 * 24 * 60 * 60 * 1000)
  )
  const last30Days = signals.filter(
    (s) => new Date(s.timestamp) >= new Date(now - 30 * 24 * 60 * 60 * 1000)
  )

  const categoryCounts = {}
  const severityCounts = { critical: 0, high: 0, medium: 0, low: 0 }
  const entityCounts = {}

  for (const signal of signals) {
    // Category
    categoryCounts[signal.category] =
      (categoryCounts[signal.category] || 0) + 1
    // Severity
    if (signal.severity) {
      severityCounts[signal.severity] =
        (severityCounts[signal.severity] || 0) + 1
    }
    // Entities
    if (signal.affectedEntities) {
      for (const entity of signal.affectedEntities) {
        entityCounts[entity] = (entityCounts[entity] || 0) + 1
      }
    }
  }

  // Top 10 entities by signal count
  const topEntities = Object.entries(entityCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([name, count]) => ({ name, count }))

  return {
    updatedAt: now.toISOString(),
    totalSignals: signals.length,
    last7Days: last7Days.length,
    last30Days: last30Days.length,
    categoryCounts,
    severityCounts,
    topEntities,
  }
}

/**
 * Main execution
 */
async function main() {
  try {
    const rawSignals = await fetchManipulationSignals()
    const enrichedSignals = enrichSignals(rawSignals)
    await saveSignals(enrichedSignals)
    console.log("[WashWatch] Update completed successfully")
  } catch (error) {
    console.error("[WashWatch] Update failed:", error.message)
    process.exit(1)
  }
}

main()
