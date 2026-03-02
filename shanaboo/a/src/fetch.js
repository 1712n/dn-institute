/**
 * 🌰 ChestnutAI – Fetch & analyze on-chain + social signals
 */
import "dotenv/config";
import axios from "axios";
import { Octokit } from "@octokit/rest";
import { ethers } from "ethers";
import fs from "fs";

const octokit = new Octokit({ auth: process.env.GITHUB_TOKEN });

// 🌰 1. Detect on-chain anomalies via Etherscan
async function fetchAnomalies() {
  const url = `https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey=${process.env.ETHERSCAN_KEY}`;
  const { data } = await axios.get(url);
  const gas = data.result;
  const anomaly = Number(gas.FastGasPrice) > 100;
  return { anomaly, gas };
}

// 🌰 2. Scan GitHub for trending crypto repos
async function fetchGitHubTrending() {
  const { data } = await octokit.rest.search.repos({
    q: "language:solidity stars:>100 pushed:>2024-01-01",
    per_page: 5,
  });
  return data.items.map((r) => ({
    name: r.full_name,
    url: r.html_url,
    stars: r.stargazers_count,
  }));
}

// 🌰 3. Query Dune for DEX volume spikes
async function fetchDuneSpike() {
  const duneQueryId = 3092718; // 🌰 example: daily DEX volume
  const { data } = await axios.post(
    "https://api.dune.com/api/v1/query/3092718/execute",
    {},
    {
      headers: { "X-Dune-API-Key": process.env.DUNE_API_KEY },
    }
  );
  return data;
}

// 🌰 4. Summarize with GitHub Models
async function summarize(payload) {
  const { data } = await axios.post(
    "https://models.inference.ai.azure.com/chat/completions",
    {
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content:
            "You are ChestnutAI 🌰. Summarize crypto narratives in 3 bullet points, max 280 chars each.",
        },
        { role: "user", content: JSON.stringify(payload) },
      ],
    },
    {
      headers: {
        Authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
        "Content-Type": "application/json",
      },
    }
  );
  return data.choices[0].message.content;
}

(async () => {
  const [anomaly, trending, spike] = await Promise.all([
    fetchAnomalies(),
    fetchGitHubTrending(),
    fetchDuneSpike(),
  ]);
  const summary = await summarize({ anomaly, trending, spike });
  fs.writeFileSync(
    "./_data/narrative.json",
    JSON.stringify({ summary, timestamp: new Date().toISOString() }, null, 2)
  );
  console.log("🌰 Narrative updated:", summary);
})();