/**
 * 🌰 ChestnutAI – Post narrative threads to X/Twitter
 */
import "dotenv/config";
import { TwitterApi } from "twitter-api-v2";
import fs from "fs";

const client = new TwitterApi({
  appKey: process.env.TWITTER_API_KEY,
  appSecret: process.env.TWITTER_API_SECRET,
  accessToken: process.env.TWITTER_ACCESS_TOKEN,
  accessSecret: process.env.TWITTER_ACCESS_SECRET,
});

(async () => {
  const { summary } = JSON.parse(
    fs.readFileSync("./_data/narrative.json", "utf8")
  );
  const lines = summary.split("\n").filter(Boolean);
  let lastId = null;
  for (const line of lines) {
    const { data } = await client.v2.tweet(line, {
      ...(lastId && { reply: { in_reply_to_tweet_id: lastId } }),
    });
    lastId = data.id;
  }
  console.log("🌰 Thread posted!");
})();