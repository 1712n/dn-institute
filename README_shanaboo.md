--- a/README.md
+++ b/README.md
@@ -1,2 +1,65 @@
-# dn-institute
-Decentralized News Institute
+# 🌰 ChestnutAI – Real-Time Crypto Sentiment & Risk Engine 🌰
+
+> A GitHub-hosted AI product that ingests live crypto-twitter & on-chain data, scores market sentiment, and surfaces **risk events** before they hit the headlines.  
+> Built with GitHub Models, Actions, Pages, and a sprinkle of chestnut magic 🌰.
+
+---
+
+## 🚀 Live Demo
+
+https://1712n.github.io/chestnut-ai/
+
+---
+
+## 🧠 What it does
+
+1. **Ingest**  
+   - Twitter API v2 filtered stream (`bitcoin`, `ethereum`, `solana`, `hack`, `exploit`, `rug`, etc.)  
+   - On-chain alerts (large inflows to CEX, unusual contract interactions) via [QuickNode](https://www.quicknode.com/) webhooks.
+
+2. **Analyze**  
+   - Sentiment & risk classification using **GitHub Models** (`gpt-4o-mini` + `text-embedding-3-small`).  
+   - Prompt template stored in `.github/prompts/risk-scorer.txt` 🌰.
+
+3. **Surface**  
+   - Auto-generate a markdown brief every 6 hours via GitHub Actions.  
+   - Push to `docs/` → GitHub Pages → static site with charts (Chart.js) and shareable cards.
+
+4. **Social**  
+   - Auto-tweet top risk events via [@ChestnutAI](https://twitter.com/ChestnutAI) (OAuth2 in GitHub Secrets).  
+   - Telegram bot (`/risk` command) deployed on Fly.io.
+
+---
+
+## 🏗️ Architecture
+
+