import { readFile } from "fs/promises"

/**
 * DeFi Sentinel - Social Media Bot
 *
 * Posts weekly DeFi exploit intelligence summaries to X (Twitter).
 * Reads the AI-generated weekly summary and formats it for social media.
 */

const TWITTER_BEARER_TOKEN = process.env.TWITTER_BEARER_TOKEN
const TWITTER_API_KEY = process.env.TWITTER_API_KEY
const TWITTER_API_SECRET = process.env.TWITTER_API_SECRET
const TWITTER_ACCESS_TOKEN = process.env.TWITTER_ACCESS_TOKEN
const TWITTER_ACCESS_SECRET = process.env.TWITTER_ACCESS_SECRET

/**
 * Format the weekly summary into a tweet thread
 * @param {Object} summary - Weekly summary from data/weekly-summary.json
 * @param {Object} stats - Stats from data/stats.json
 * @returns {Array<string>} Array of tweet texts
 */
function formatTweetThread(summary, stats) {
  const tweets = []

  // Main tweet
  const riskEmoji =
    {
      ELEVATED: "\u{1F534}",
      MODERATE: "\u{1F7E1}",
      LOW: "\u{1F7E2}",
      UNKNOWN: "\u{26AA}",
    }[summary.riskLevel] || "\u{26AA}"

  const mainTweet = `${riskEmoji} DeFi Sentinel Weekly Brief

${summary.summary || "Weekly DeFi security intelligence update."}

Events tracked: ${summary.totalEvents}
Risk Level: ${summary.riskLevel || "N/A"}

#DeFi #Security #Web3 #CryptoSecurity`

  tweets.push(mainTweet)

  // Top threats tweet
  if (summary.topThreats && summary.topThreats.length > 0) {
    const threatList = summary.topThreats.map((t) => `\u{2022} ${t.name}: ${t.description}`).join("\n")

    tweets.push(`\u{1F6A8} Top Threats This Week:\n\n${threatList}`)
  }

  // Severity breakdown tweet
  if (stats && stats.bySeverity) {
    const sevLines = Object.entries(stats.bySeverity)
      .sort(([, a], [, b]) => b - a)
      .map(([sev, count]) => {
        const emoji = { CRITICAL: "\u{1F534}", HIGH: "\u{1F7E0}", MEDIUM: "\u{1F7E1}", LOW: "\u{1F7E2}" }[sev] || "\u{26AA}"
        return `${emoji} ${sev}: ${count}`
      })
      .join("\n")

    tweets.push(`\u{1F4CA} Severity Breakdown:\n\n${sevLines}\n\nFull report: https://github.com/${process.env.GITHUB_REPOSITORY || "1712n/dn-institute"}`)
  }

  // Recommendations tweet
  if (summary.recommendations && summary.recommendations.length > 0) {
    const recs = summary.recommendations
      .slice(0, 3)
      .map((r) => `\u{1F6E1}\u{FE0F} ${r}`)
      .join("\n")

    tweets.push(`Security Recommendations:\n\n${recs}\n\nStay safe out there! \u{1F512}`)
  }

  return tweets
}

/**
 * Post a tweet using Twitter API v2
 * @param {string} text - Tweet text
 * @param {string|null} replyToId - ID of tweet to reply to (for threads)
 * @returns {Promise<string>} Tweet ID
 */
async function postTweet(text, replyToId = null) {
  const url = "https://api.twitter.com/2/tweets"

  const body = { text }
  if (replyToId) {
    body.reply = { in_reply_to_tweet_id: replyToId }
  }

  // Using OAuth 2.0 Bearer Token for app-only auth
  // For user-context posting, OAuth 1.0a would be needed
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${TWITTER_BEARER_TOKEN}`,
    },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    const errText = await response.text()
    throw new Error(`Twitter API error (${response.status}): ${errText}`)
  }

  const data = await response.json()
  return data.data.id
}

/**
 * Main posting workflow
 */
async function postToTwitter() {
  try {
    if (!TWITTER_BEARER_TOKEN) {
      console.log("TWITTER_BEARER_TOKEN not set - skipping social media post")
      console.log("To enable Twitter posting, add TWITTER_BEARER_TOKEN to repository secrets")
      return
    }

    // Load data
    const summaryRaw = await readFile("data/weekly-summary.json", "utf-8")
    const summary = JSON.parse(summaryRaw)

    let stats = null
    try {
      const statsRaw = await readFile("data/stats.json", "utf-8")
      stats = JSON.parse(statsRaw)
    } catch {
      // Stats file may not exist
    }

    // Format tweets
    const tweets = formatTweetThread(summary, stats)

    console.log(`Posting ${tweets.length} tweets...`)
    tweets.forEach((t, i) => {
      console.log(`\n--- Tweet ${i + 1} ---`)
      console.log(t)
    })

    // Post thread
    let previousTweetId = null
    for (let i = 0; i < tweets.length; i++) {
      console.log(`\nPosting tweet ${i + 1}/${tweets.length}...`)
      previousTweetId = await postTweet(tweets[i], previousTweetId)
      console.log(`  Posted: ${previousTweetId}`)

      // Rate limiting
      if (i < tweets.length - 1) {
        await new Promise((resolve) => setTimeout(resolve, 2000))
      }
    }

    console.log("\nTwitter thread posted successfully!")
  } catch (error) {
    console.error("Twitter posting failed:", error.message)
    // Don't exit with error - social media posting is non-critical
  }
}

postToTwitter()
