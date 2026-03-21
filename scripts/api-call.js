import { writeFile, readFile, mkdir } from "fs/promises"

const API_URL = "https://cpw-tracker.p.rapidapi.com/"
const API_KEY = process.env.RAPIDAPI_KEY

if (!API_KEY) {
  console.error("Error: RAPIDAPI_KEY environment variable is required")
  process.exit(1)
}

/**
 * Get start and end dates for data fetch
 * Fetches last 7 days of DeFi exploit intelligence
 * @returns {Object} Object with startTime and endTime ISO strings
 */
function getDateRange() {
  const now = new Date()
  const endTime = now
  const startTime = new Date(now)
  startTime.setDate(startTime.getDate() - 7) // Last 7 days for weekly briefing
  return {
    startTime: startTime.toISOString(),
    endTime: endTime.toISOString(),
  }
}

/**
 * Fetch DeFi exploit signals from CPW API
 * Monitors multiple entity types for comprehensive coverage
 * @returns {Promise<Array>} Array of exploit event objects
 */
async function fetchExploitSignals() {
  const { startTime, endTime } = getDateRange()

  // Monitor multiple facets of DeFi security
  const queries = [
    { entities: "DeFi protocols", topic: "exploit" },
    { entities: "smart contracts", topic: "vulnerability" },
    { entities: "blockchain bridges", topic: "hack" },
    { entities: "decentralized exchanges", topic: "security breach" },
  ]

  console.log(`Fetching DeFi exploit intelligence for: ${startTime} to ${endTime}`)

  const allResults = []

  for (const query of queries) {
    try {
      console.log(`  Querying: ${query.entities} / ${query.topic}`)
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
          startTime,
          endTime,
        }),
      })

      if (!response.ok) {
        console.warn(`  Warning: Query failed with status ${response.status} for ${query.entities}/${query.topic}`)
        continue
      }

      const data = await response.json()
      const results = Array.isArray(data) ? data : []
      console.log(`  Found ${results.length} results for ${query.entities}/${query.topic}`)

      // Tag each result with its query category
      const tagged = results.map((item) => ({
        ...item,
        category: query.entities,
        threatType: query.topic,
      }))

      allResults.push(...tagged)
    } catch (err) {
      console.warn(`  Warning: Query error for ${query.entities}/${query.topic}: ${err.message}`)
    }
  }

  // Deduplicate by eventSummary similarity
  const seen = new Set()
  const unique = allResults.filter((item) => {
    const key = (item.eventSummary || "").substring(0, 100)
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })

  console.log(`Total unique results: ${unique.length}`)
  return unique
}

/**
 * Merge new events with existing data, keeping last 30 days
 * @param {Array} newEvents - Newly fetched events
 * @returns {Array} Merged and deduplicated events
 */
async function mergeWithExisting(newEvents) {
  let existing = []
  try {
    const raw = await readFile("data/events.json", "utf-8")
    existing = JSON.parse(raw)
  } catch {
    // No existing data file
  }

  const thirtyDaysAgo = new Date()
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)

  const all = [...newEvents, ...existing]

  // Deduplicate
  const seen = new Set()
  const unique = all.filter((item) => {
    const key = (item.eventSummary || "").substring(0, 100)
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })

  // Keep only last 30 days
  return unique.filter((item) => {
    const ts = new Date(item.timestamp)
    return ts >= thirtyDaysAgo
  })
}

/**
 * Save event data to JSON file
 * @param {Array} data - Array of event objects
 */
async function saveData(data) {
  const sorted = data.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))

  await mkdir("data", { recursive: true })
  await writeFile("data/events.json", JSON.stringify(sorted, null, 2))

  console.log(`Saved ${sorted.length} events to data/events.json`)
}

/**
 * Main update process
 */
async function updateData() {
  try {
    const newEvents = await fetchExploitSignals()
    const merged = await mergeWithExisting(newEvents)
    await saveData(merged)
    console.log("DeFi Sentinel data update completed successfully")
  } catch (error) {
    console.error("Update failed:", error.message)
    process.exit(1)
  }
}

updateData()
