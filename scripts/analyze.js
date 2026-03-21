import { readFile, writeFile, mkdir } from "fs/promises"

/**
 * DeFi Sentinel - AI-Powered Threat Analysis
 *
 * Uses GitHub Models (GPT-4o) to analyze DeFi exploit events and generate:
 * - Severity ratings for each incident
 * - Attack vector classification
 * - Weekly trend analysis and threat landscape summary
 * - Actionable security recommendations
 */

const GITHUB_TOKEN = process.env.GITHUB_TOKEN
const MODEL_ENDPOINT = "https://models.inference.ai.azure.com"
const MODEL_NAME = "gpt-4o"

if (!GITHUB_TOKEN) {
  console.error("Error: GITHUB_TOKEN environment variable is required for GitHub Models")
  process.exit(1)
}

/**
 * Call GitHub Models API
 * @param {string} systemPrompt - System message
 * @param {string} userPrompt - User message
 * @returns {Promise<string>} Model response
 */
async function callModel(systemPrompt, userPrompt) {
  const response = await fetch(`${MODEL_ENDPOINT}/chat/completions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${GITHUB_TOKEN}`,
    },
    body: JSON.stringify({
      model: MODEL_NAME,
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userPrompt },
      ],
      temperature: 0.3,
      max_tokens: 2000,
    }),
  })

  if (!response.ok) {
    const errText = await response.text()
    throw new Error(`GitHub Models API error (${response.status}): ${errText}`)
  }

  const data = await response.json()
  return data.choices[0].message.content
}

/**
 * Analyze a single exploit event for severity and classification
 * @param {Object} event - Event object from events.json
 * @returns {Promise<Object>} Enriched event with AI analysis
 */
async function analyzeEvent(event) {
  const systemPrompt = `You are a DeFi security analyst. Analyze the following security event and provide a JSON response with these fields:
- "severity": one of "CRITICAL", "HIGH", "MEDIUM", "LOW"
- "attackVector": brief classification of the attack type (e.g., "Flash Loan Attack", "Reentrancy", "Oracle Manipulation", "Bridge Exploit", "Phishing", "Rug Pull", "Access Control", "Unknown")
- "estimatedImpact": brief description of financial/operational impact
- "affectedProtocols": array of protocol/project names mentioned
- "recommendation": one-sentence security recommendation

Respond ONLY with valid JSON, no markdown formatting.`

  const userPrompt = `Analyze this DeFi security event:
Category: ${event.category || "Unknown"}
Threat Type: ${event.threatType || "Unknown"}
Timestamp: ${event.timestamp}
Summary: ${event.eventSummary}`

  try {
    const analysisText = await callModel(systemPrompt, userPrompt)
    const analysis = JSON.parse(analysisText.replace(/```json\n?|\n?```/g, "").trim())
    return { ...event, analysis }
  } catch (err) {
    console.warn(`  Warning: Analysis failed for event: ${err.message}`)
    return {
      ...event,
      analysis: {
        severity: "UNKNOWN",
        attackVector: "Unclassified",
        estimatedImpact: "Unable to determine",
        affectedProtocols: [],
        recommendation: "Manual review recommended",
      },
    }
  }
}

/**
 * Generate weekly threat landscape summary
 * @param {Array} events - All analyzed events
 * @returns {Promise<Object>} Weekly summary object
 */
async function generateWeeklySummary(events) {
  if (events.length === 0) {
    return {
      generatedAt: new Date().toISOString(),
      totalEvents: 0,
      summary: "No DeFi security events detected this week.",
      topThreats: [],
      trendAnalysis: "Insufficient data for trend analysis.",
      recommendations: [],
    }
  }

  const eventDescriptions = events
    .slice(0, 20)
    .map(
      (e, i) =>
        `${i + 1}. [${e.analysis?.severity || "UNKNOWN"}] ${e.analysis?.attackVector || "Unknown"}: ${(e.eventSummary || "").substring(0, 200)}`
    )
    .join("\n")

  const systemPrompt = `You are a senior DeFi security intelligence analyst writing a weekly threat briefing. Provide a JSON response with:
- "summary": 2-3 sentence executive summary of this week's DeFi threat landscape
- "topThreats": array of top 3 threat categories with "name" and "description" fields
- "trendAnalysis": 2-3 sentences analyzing trends and patterns
- "riskLevel": overall weekly risk level ("ELEVATED", "MODERATE", "LOW")
- "recommendations": array of 3-5 actionable security recommendations (strings)

Respond ONLY with valid JSON, no markdown formatting.`

  const userPrompt = `Generate a weekly DeFi security intelligence briefing based on these ${events.length} events from the past week:\n\n${eventDescriptions}`

  try {
    const summaryText = await callModel(systemPrompt, userPrompt)
    const summary = JSON.parse(summaryText.replace(/```json\n?|\n?```/g, "").trim())
    return {
      generatedAt: new Date().toISOString(),
      totalEvents: events.length,
      ...summary,
    }
  } catch (err) {
    console.error(`Weekly summary generation failed: ${err.message}`)
    return {
      generatedAt: new Date().toISOString(),
      totalEvents: events.length,
      summary: "Weekly summary generation encountered an error. Please review individual events.",
      topThreats: [],
      trendAnalysis: "Unable to generate trend analysis.",
      riskLevel: "UNKNOWN",
      recommendations: ["Review individual event reports for details."],
    }
  }
}

/**
 * Main analysis pipeline
 */
async function runAnalysis() {
  try {
    // Load events
    const raw = await readFile("data/events.json", "utf-8")
    const events = JSON.parse(raw)

    if (events.length === 0) {
      console.log("No events to analyze")
      return
    }

    console.log(`Analyzing ${events.length} DeFi security events with GitHub Models (${MODEL_NAME})...`)

    // Analyze each event (with rate limiting)
    const analyzed = []
    for (let i = 0; i < events.length; i++) {
      console.log(`  Analyzing event ${i + 1}/${events.length}...`)
      const result = await analyzeEvent(events[i])
      analyzed.push(result)

      // Rate limiting: small delay between API calls
      if (i < events.length - 1) {
        await new Promise((resolve) => setTimeout(resolve, 1000))
      }
    }

    // Save analyzed events
    await mkdir("data", { recursive: true })
    await writeFile("data/events.json", JSON.stringify(analyzed, null, 2))
    console.log(`Saved ${analyzed.length} analyzed events`)

    // Generate weekly summary
    console.log("Generating weekly threat intelligence summary...")
    const summary = await generateWeeklySummary(analyzed)
    await writeFile("data/weekly-summary.json", JSON.stringify(summary, null, 2))
    console.log("Weekly summary saved to data/weekly-summary.json")

    // Generate severity stats
    const stats = {
      generatedAt: new Date().toISOString(),
      total: analyzed.length,
      bySeverity: {},
      byAttackVector: {},
      byCategory: {},
    }

    for (const event of analyzed) {
      const sev = event.analysis?.severity || "UNKNOWN"
      const vec = event.analysis?.attackVector || "Unknown"
      const cat = event.category || "Unknown"
      stats.bySeverity[sev] = (stats.bySeverity[sev] || 0) + 1
      stats.byAttackVector[vec] = (stats.byAttackVector[vec] || 0) + 1
      stats.byCategory[cat] = (stats.byCategory[cat] || 0) + 1
    }

    await writeFile("data/stats.json", JSON.stringify(stats, null, 2))
    console.log("Statistics saved to data/stats.json")

    console.log("DeFi Sentinel analysis pipeline completed successfully")
  } catch (error) {
    console.error("Analysis failed:", error.message)
    process.exit(1)
  }
}

runAnalysis()
