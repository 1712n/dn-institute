import { readFile, writeFile, mkdir } from "fs/promises"

const GITHUB_TOKEN = process.env.GITHUB_TOKEN
const MODEL = "gpt-4o-mini"
const ENDPOINT = "https://models.inference.ai.azure.com/chat/completions"

if (!GITHUB_TOKEN) {
  console.error("Error: GITHUB_TOKEN environment variable is required")
  process.exit(1)
}

/**
 * Sends a prompt to GitHub Models and returns the response text.
 * @param {string} systemPrompt
 * @param {string} userPrompt
 * @returns {Promise<string>}
 */
async function queryModel(systemPrompt, userPrompt) {
  const response = await fetch(ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${GITHUB_TOKEN}`
    },
    body: JSON.stringify({
      model: MODEL,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userPrompt }
      ],
      temperature: 0.3,
      max_tokens: 2000
    })
  })

  if (!response.ok) {
    const body = await response.text()
    throw new Error(`GitHub Models API error ${response.status}: ${body}`)
  }

  const data = await response.json()
  return data.choices?.[0]?.message?.content || ""
}

/**
 * Loads events from data/events.json.
 * @returns {Promise<Array>}
 */
async function loadEvents() {
  try {
    const raw = await readFile("data/events.json", "utf-8")
    return JSON.parse(raw)
  } catch {
    console.error("No events.json found. Run api-call.js first.")
    process.exit(1)
  }
}

/**
 * Pass 1: AI-powered severity rating and risk scoring for each event.
 * Processes events in batches to avoid token limits.
 * @param {Array} events
 * @returns {Promise<Array>}
 */
async function enrichEvents(events) {
  const unscored = events.filter(e => !e.severity)

  if (unscored.length === 0) {
    console.log("All events already have severity ratings. Skipping enrichment.")
    return events
  }

  console.log(`Enriching ${unscored.length} events with AI severity analysis...`)

  const batchSize = 10
  const batches = []
  for (let i = 0; i < unscored.length; i += batchSize) {
    batches.push(unscored.slice(i, i + batchSize))
  }

  for (let i = 0; i < batches.length; i++) {
    const batch = batches[i]
    console.log(`  Processing batch ${i + 1}/${batches.length} (${batch.length} events)`)

    const summaries = batch.map((e, idx) => `[${idx}] ${e.eventSummary?.substring(0, 500) || "No summary"}`).join("\n\n")

    const systemPrompt = `You are a crypto fraud analyst specializing in token scams, rug pulls, Ponzi schemes, and pump-and-dump schemes. For each event, provide a JSON array of objects with:
- "index": the event index number
- "severity": one of "CRITICAL", "HIGH", "MEDIUM", "LOW"
- "riskScore": integer 0-100 (100 = maximum risk)
- "scamVector": brief label of the attack/scam method (e.g., "liquidity drain", "fake audit", "social engineering", "contract backdoor")
- "impactEstimate": brief string estimating financial impact if mentioned (e.g., "$2.5M stolen", "unknown", "50+ victims")

Rate severity based on: financial losses mentioned, number of victims, sophistication of scam, and whether the scam is ongoing vs resolved.

Return ONLY valid JSON array. No markdown, no explanation.`

    const userPrompt = `Analyze these crypto token scam events:\n\n${summaries}`

    try {
      const result = await queryModel(systemPrompt, userPrompt)
      const cleaned = result.replace(/```json\n?/g, "").replace(/```\n?/g, "").trim()
      const ratings = JSON.parse(cleaned)

      for (const rating of ratings) {
        const event = batch[rating.index]
        if (event) {
          event.severity = rating.severity
          event.riskScore = rating.riskScore
          event.scamVector = rating.scamVector
          event.impactEstimate = rating.impactEstimate
        }
      }
    } catch (err) {
      console.error(`  Batch ${i + 1} analysis failed: ${err.message}`)
      // Assign default ratings for failed batches
      for (const event of batch) {
        if (!event.severity) {
          event.severity = "MEDIUM"
          event.riskScore = 50
          event.scamVector = "unclassified"
          event.impactEstimate = "unknown"
        }
      }
    }
  }

  return events
}

/**
 * Pass 2: Generate a weekly intelligence brief summarizing scam trends.
 * @param {Array} events
 * @returns {Promise<Object>}
 */
async function generateBrief(events) {
  console.log("Generating weekly intelligence brief...")

  // Collect stats for the brief
  const scamTypes = {}
  const severityCounts = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 }
  const entities = new Set()

  for (const event of events) {
    const type = event.scamType || "general-scam"
    scamTypes[type] = (scamTypes[type] || 0) + 1

    const sev = event.severity || "MEDIUM"
    if (severityCounts[sev] !== undefined) severityCounts[sev]++

    if (event.entities) {
      event.entities.split(",").map(e => e.trim()).forEach(e => entities.add(e))
    }
  }

  const statsBlock = `
Total events: ${events.length}
Severity breakdown: CRITICAL=${severityCounts.CRITICAL}, HIGH=${severityCounts.HIGH}, MEDIUM=${severityCounts.MEDIUM}, LOW=${severityCounts.LOW}
Scam types: ${Object.entries(scamTypes).map(([k, v]) => `${k}=${v}`).join(", ")}
Entities mentioned: ${[...entities].slice(0, 20).join(", ")}
  `.trim()

  const recentSummaries = events
    .slice(0, 15)
    .map(e => `- [${e.severity || "?"}] [${e.scamType || "?"}] ${e.eventSummary?.substring(0, 300) || "N/A"}`)
    .join("\n")

  const systemPrompt = `You are a senior crypto threat intelligence analyst writing a weekly brief on token scams and fraud. Write a professional intelligence brief in JSON format with:
- "title": brief title for this week's report
- "riskLevel": overall risk assessment ("LOW", "ELEVATED", "HIGH", "CRITICAL")
- "summary": 2-3 paragraph executive summary of the week's token scam landscape
- "keyFindings": array of 3-5 key findings (strings)
- "trendAnalysis": 1-2 paragraphs on emerging scam trends and patterns
- "recommendations": array of 3-5 actionable recommendations for crypto investors
- "generatedAt": current ISO timestamp

Return ONLY valid JSON. No markdown.`

  const userPrompt = `Generate a weekly token scam intelligence brief based on this data:

${statsBlock}

Recent events:
${recentSummaries}`

  try {
    const result = await queryModel(systemPrompt, userPrompt)
    const cleaned = result.replace(/```json\n?/g, "").replace(/```\n?/g, "").trim()
    return JSON.parse(cleaned)
  } catch (err) {
    console.error(`Brief generation failed: ${err.message}`)
    return {
      title: "Weekly Token Scam Intelligence Brief",
      riskLevel: severityCounts.CRITICAL > 0 ? "HIGH" : "ELEVATED",
      summary: `This week we tracked ${events.length} token scam events across multiple categories. ${severityCounts.CRITICAL} critical and ${severityCounts.HIGH} high-severity incidents were identified.`,
      keyFindings: [
        `${events.length} total scam events detected this period`,
        `${severityCounts.CRITICAL + severityCounts.HIGH} high-impact incidents requiring attention`,
        `Most common scam type: ${Object.entries(scamTypes).sort((a, b) => b[1] - a[1])[0]?.[0] || "general-scam"}`
      ],
      trendAnalysis: "AI analysis unavailable. Review individual events for detailed assessment.",
      recommendations: [
        "Verify smart contract audits before interacting with new tokens",
        "Check liquidity lock status on any new token launch",
        "Be cautious of tokens with anonymous teams and no verifiable track record",
        "Monitor on-chain activity for large insider movements before public announcements"
      ],
      generatedAt: new Date().toISOString()
    }
  }
}

/**
 * Loads historical briefs for trend tracking.
 * @returns {Promise<Array>}
 */
async function loadHistory() {
  try {
    const raw = await readFile("data/history.json", "utf-8")
    return JSON.parse(raw)
  } catch {
    return []
  }
}

/**
 * Main analysis pipeline.
 */
async function runAnalysis() {
  console.log("TokenScam Shield - AI Analysis Pipeline\n")

  const events = await loadEvents()
  console.log(`Loaded ${events.length} events\n`)

  // Pass 1: Enrich events with severity ratings
  const enriched = await enrichEvents(events)

  // Save enriched events back
  await mkdir("data", { recursive: true })
  await writeFile("data/events.json", JSON.stringify(enriched, null, 2))
  console.log(`\nSaved enriched events to data/events.json`)

  // Pass 2: Generate intelligence brief
  const brief = await generateBrief(enriched)

  // Save analysis
  await writeFile("data/analysis.json", JSON.stringify(brief, null, 2))
  console.log(`Saved intelligence brief to data/analysis.json`)

  // Append to history (rolling 52-week archive)
  const history = await loadHistory()
  history.unshift({
    ...brief,
    eventCount: enriched.length,
    timestamp: new Date().toISOString()
  })
  const trimmed = history.slice(0, 52)
  await writeFile("data/history.json", JSON.stringify(trimmed, null, 2))
  console.log(`Updated history archive (${trimmed.length} weeks)`)

  console.log("\nAnalysis pipeline complete.")
}

runAnalysis().catch(err => {
  console.error("Analysis failed:", err.message)
  process.exit(1)
})
