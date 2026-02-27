import { writeFile, readFile, mkdir } from "fs/promises"

const API_URL = "https://cpw-tracker.p.rapidapi.com/"
const API_KEY = process.env.RAPIDAPI_KEY

if (!API_KEY) {
  console.error("Error: RAPIDAPI_KEY environment variable is required")
  process.exit(1)
}

/**
 * Query configurations for multi-topic token scam monitoring.
 * Each query targets a different scam vector in the crypto token space.
 */
const QUERIES = [
  {
    entities: "cryptocurrency tokens",
    topic: "scam",
    label: "token-scams"
  },
  {
    entities: "cryptocurrency tokens",
    topic: "fraud",
    label: "token-fraud"
  },
  {
    entities: "decentralized exchanges",
    topic: "rug pull",
    label: "dex-rugpulls"
  },
  {
    entities: "cryptocurrency projects",
    topic: "ponzi scheme",
    label: "ponzi-schemes"
  },
  {
    entities: "cryptocurrency tokens",
    topic: "pump and dump",
    label: "pump-dumps"
  }
]

/**
 * Returns ISO date strings for the past 7 days.
 * @returns {{ startTime: string, endTime: string }}
 */
function getDateRange() {
  const now = new Date()
  const start = new Date(now)
  start.setDate(start.getDate() - 7)
  return {
    startTime: start.toISOString(),
    endTime: now.toISOString()
  }
}

/**
 * Fetches events from the CPW Tracker API for a given query config.
 * @param {{ entities: string, topic: string, label: string }} query
 * @param {{ startTime: string, endTime: string }} dateRange
 * @returns {Promise<Array>}
 */
async function fetchQuery(query, dateRange) {
  console.log(`  [${query.label}] Fetching: entities="${query.entities}", topic="${query.topic}"`)

  const response = await fetch(API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-rapidapi-host": "cpw-tracker.p.rapidapi.com",
      "x-rapidapi-key": API_KEY,
    },
    body: JSON.stringify({
      entities: query.entities,
      topic: query.topic,
      startTime: dateRange.startTime,
      endTime: dateRange.endTime
    }),
  })

  if (!response.ok) {
    console.error(`  [${query.label}] API error: ${response.status}`)
    return []
  }

  const data = await response.json()
  const results = Array.isArray(data) ? data : []

  // Tag each result with the query label for category tracking
  const tagged = results.map(item => ({
    ...item,
    _queryLabel: query.label
  }))

  console.log(`  [${query.label}] Found ${tagged.length} events`)
  return tagged
}

/**
 * Deduplicates events by comparing their eventSummary content.
 * Uses a normalized hash of the first 200 characters of each summary.
 * @param {Array} events
 * @returns {Array}
 */
function deduplicateEvents(events) {
  const seen = new Set()
  const unique = []

  for (const event of events) {
    const key = (event.eventSummary || "")
      .substring(0, 200)
      .toLowerCase()
      .replace(/\s+/g, " ")
      .trim()

    if (!seen.has(key)) {
      seen.add(key)
      unique.push(event)
    }
  }

  return unique
}

/**
 * Classifies the scam type based on event content and query label.
 * @param {{ _queryLabel: string, eventSummary: string, topic: string }} event
 * @returns {string}
 */
function classifyScamType(event) {
  const summary = (event.eventSummary || "").toLowerCase()
  const label = event._queryLabel || ""

  if (label.includes("rugpull") || summary.includes("rug pull") || summary.includes("rugpull")) {
    return "rug-pull"
  }
  if (label.includes("ponzi") || summary.includes("ponzi") || summary.includes("pyramid")) {
    return "ponzi-scheme"
  }
  if (label.includes("pump") || summary.includes("pump and dump") || summary.includes("pump-and-dump")) {
    return "pump-and-dump"
  }
  if (summary.includes("honeypot") || summary.includes("honey pot")) {
    return "honeypot-token"
  }
  if (summary.includes("phishing") || summary.includes("fake airdrop")) {
    return "phishing"
  }
  if (summary.includes("exit scam")) {
    return "exit-scam"
  }
  return "general-scam"
}

/**
 * Extracts source URLs from event summaries.
 * @param {string} summary
 * @returns {string[]}
 */
function extractSources(summary) {
  if (!summary) return []
  const urlRegex = /https?:\/\/[^\s)}\]"']+/g
  return [...new Set(summary.match(urlRegex) || [])]
}

/**
 * Loads existing events from disk for merge-based history tracking.
 * @returns {Promise<Array>}
 */
async function loadExistingEvents() {
  try {
    const raw = await readFile("data/events.json", "utf-8")
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

/**
 * Merges new events with existing ones, deduplicates, and caps at 300 events.
 * @param {Array} existing
 * @param {Array} fresh
 * @returns {Array}
 */
function mergeEvents(existing, fresh) {
  const combined = [...fresh, ...existing]
  const deduped = deduplicateEvents(combined)
  const sorted = deduped.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
  return sorted.slice(0, 300)
}

/**
 * Main pipeline: fetch from all queries, deduplicate, classify, merge, and save.
 */
async function updateData() {
  const dateRange = getDateRange()

  console.log(`TokenScam Shield - Data Pipeline`)
  console.log(`Period: ${dateRange.startTime} to ${dateRange.endTime}`)
  console.log(`Running ${QUERIES.length} queries...\n`)

  const allResults = []

  for (const query of QUERIES) {
    const results = await fetchQuery(query, dateRange)
    allResults.push(...results)
  }

  console.log(`\nTotal raw events: ${allResults.length}`)

  const deduped = deduplicateEvents(allResults)
  console.log(`After deduplication: ${deduped.length}`)

  // Enrich each event with scam classification and extracted sources
  const enriched = deduped.map(event => ({
    timestamp: event.timestamp,
    entities: event.entities,
    topic: event.topic,
    eventSummary: event.eventSummary,
    scamType: classifyScamType(event),
    sources: extractSources(event.eventSummary),
    _queryLabel: event._queryLabel
  }))

  const existing = await loadExistingEvents()
  const merged = mergeEvents(existing, enriched)

  await mkdir("data", { recursive: true })
  await writeFile("data/events.json", JSON.stringify(merged, null, 2))

  console.log(`\nSaved ${merged.length} events to data/events.json`)
  console.log("Data pipeline complete.")
}

updateData().catch(err => {
  console.error("Pipeline failed:", err.message)
  process.exit(1)
})
