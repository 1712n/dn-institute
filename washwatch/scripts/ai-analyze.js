// WashWatch - AI Analysis Module
// Uses GitHub Models (OpenAI-compatible) to generate intelligence briefs
// from raw market manipulation signals

import { readFile, writeFile, mkdir } from "fs/promises"

const GITHUB_TOKEN = process.env.GITHUB_TOKEN
const MODEL_ENDPOINT =
  "https://models.inference.ai.azure.com/chat/completions"

/**
 * Generate AI analysis of market manipulation signals
 * Uses GitHub Models for inference (free with GitHub account)
 * @param {Array} signals - Array of signal objects
 * @returns {Promise<Object>} AI-generated analysis
 */
async function analyzeWithAI(signals) {
  if (!GITHUB_TOKEN) {
    console.log(
      "[WashWatch AI] No GITHUB_TOKEN found, generating rule-based analysis"
    )
    return generateRuleBasedAnalysis(signals)
  }

  const signalSummaries = signals
    .slice(0, 20) // Limit to most recent 20 for context window
    .map(
      (s, i) =>
        `${i + 1}. [${s.category}] ${s.severity?.toUpperCase()} - ${s.entities}: ${s.eventSummary?.substring(0, 300)}`
    )
    .join("\n")

  const prompt = `You are WashWatch, a crypto market manipulation intelligence analyst.
Analyze these market manipulation signals detected in the last week and produce a concise intelligence brief.

SIGNALS:
${signalSummaries}

Produce a JSON response with this structure:
{
  "weeklyBrief": "2-3 paragraph executive summary of key manipulation trends",
  "riskLevel": "CRITICAL|HIGH|ELEVATED|MODERATE|LOW",
  "topThreats": [
    {"threat": "description", "severity": "critical|high|medium", "entities": ["affected exchanges/tokens"]}
  ],
  "recommendations": ["actionable recommendation 1", "recommendation 2"],
  "manipulationTrends": {
    "washTrading": "trend assessment",
    "spoofing": "trend assessment",
    "pumpAndDump": "trend assessment"
  }
}

Be specific, data-driven, and cite specific signals. Response must be valid JSON only.`

  try {
    const response = await fetch(MODEL_ENDPOINT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${GITHUB_TOKEN}`,
      },
      body: JSON.stringify({
        model: "gpt-4o-mini",
        messages: [
          {
            role: "system",
            content:
              "You are a crypto market surveillance analyst. Respond only with valid JSON.",
          },
          { role: "user", content: prompt },
        ],
        temperature: 0.3,
        max_tokens: 2000,
      }),
    })

    if (!response.ok) {
      throw new Error(`GitHub Models API error: ${response.status}`)
    }

    const data = await response.json()
    const content = data.choices?.[0]?.message?.content || "{}"

    // Parse the JSON response (handle markdown code blocks)
    const jsonStr = content.replace(/```json\n?/g, "").replace(/```\n?/g, "")
    const analysis = JSON.parse(jsonStr)
    analysis.generatedAt = new Date().toISOString()
    analysis.model = "gpt-4o-mini"
    analysis.signalsAnalyzed = signals.length

    return analysis
  } catch (error) {
    console.error("[WashWatch AI] AI analysis failed:", error.message)
    console.log("[WashWatch AI] Falling back to rule-based analysis")
    return generateRuleBasedAnalysis(signals)
  }
}

/**
 * Rule-based analysis fallback when AI is unavailable
 * @param {Array} signals - Array of signal objects
 * @returns {Object} Analysis object
 */
function generateRuleBasedAnalysis(signals) {
  const categoryCounts = {}
  const severityCounts = { critical: 0, high: 0, medium: 0, low: 0 }
  const entities = new Set()

  for (const signal of signals) {
    categoryCounts[signal.category] =
      (categoryCounts[signal.category] || 0) + 1
    if (signal.severity) {
      severityCounts[signal.severity]++
    }
    if (signal.affectedEntities) {
      signal.affectedEntities.forEach((e) => entities.add(e))
    }
  }

  // Determine overall risk level
  let riskLevel = "LOW"
  if (severityCounts.critical > 0) riskLevel = "CRITICAL"
  else if (severityCounts.high > 2) riskLevel = "HIGH"
  else if (severityCounts.high > 0 || severityCounts.medium > 3)
    riskLevel = "ELEVATED"
  else if (severityCounts.medium > 0) riskLevel = "MODERATE"

  const topCategory = Object.entries(categoryCounts).sort(
    (a, b) => b[1] - a[1]
  )[0]

  const brief =
    signals.length > 0
      ? `WashWatch detected ${signals.length} market manipulation signals this week across ${entities.size} entities. ` +
        `The dominant category was ${topCategory?.[0] || "unknown"} with ${topCategory?.[1] || 0} incidents. ` +
        `${severityCounts.critical} critical and ${severityCounts.high} high severity signals require immediate attention.`
      : "No significant market manipulation signals detected this reporting period. Markets appear to be operating within normal parameters."

  return {
    weeklyBrief: brief,
    riskLevel,
    topThreats: signals
      .filter((s) => s.severity === "critical" || s.severity === "high")
      .slice(0, 5)
      .map((s) => ({
        threat: s.eventSummary?.substring(0, 200) || "Unspecified threat",
        severity: s.severity,
        entities: s.affectedEntities || [],
      })),
    recommendations: [
      severityCounts.critical > 0
        ? "Immediately review critical severity signals for exposure"
        : "Continue routine monitoring",
      "Cross-reference flagged exchanges with your portfolio holdings",
      "Review Benford's Law deviation metrics for flagged trading pairs",
    ],
    manipulationTrends: {
      washTrading: `${categoryCounts["wash-trading"] || 0} signals detected`,
      spoofing: `${categoryCounts["spoofing-layering"] || 0} signals detected`,
      pumpAndDump: `${categoryCounts["pump-and-dump"] || 0} signals detected`,
    },
    generatedAt: new Date().toISOString(),
    model: "rule-based",
    signalsAnalyzed: signals.length,
  }
}

/**
 * Main execution
 */
async function main() {
  try {
    let signals = []
    try {
      const raw = await readFile("data/signals.json", "utf-8")
      signals = JSON.parse(raw)
    } catch {
      console.log("[WashWatch AI] No signals file found, using empty dataset")
    }

    // Filter to last 7 days for analysis
    const weekAgo = new Date()
    weekAgo.setDate(weekAgo.getDate() - 7)
    const recentSignals = signals.filter(
      (s) => new Date(s.timestamp) >= weekAgo
    )

    console.log(
      `[WashWatch AI] Analyzing ${recentSignals.length} signals from last 7 days`
    )

    const analysis = await analyzeWithAI(recentSignals)

    await mkdir("data", { recursive: true })
    await writeFile("data/analysis.json", JSON.stringify(analysis, null, 2))

    console.log("[WashWatch AI] Analysis saved to data/analysis.json")
    console.log(`[WashWatch AI] Risk Level: ${analysis.riskLevel}`)
  } catch (error) {
    console.error("[WashWatch AI] Analysis failed:", error.message)
    process.exit(1)
  }
}

main()
