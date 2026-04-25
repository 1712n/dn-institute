const Twitter = require('twitter');

const client = new Twitter({
  consumer_key: 'your-consumer-key',
  consumer_secret: 'your-consumer-secret',
  access_token_key: 'your-access-token-key',
  access_token_secret: 'your-access-token-secret'
});

const topics = [
  { topic: 'hacker attacks', sentiment: 'negative', notes: 'DDoS, hacks, stolen funds, etc.' },
  { topic: 'law enforcement', sentiment: 'negative', notes: 'potential litigation, enforcement actions, court proceedings, etc.' },
  { topic: 'uptime problems', sentiment: 'negative', notes: 'downtime of any sort, matching orders engine issues, freezing website, API lags, planned and unplanned maintenance, service outages, etc.' },
  { topic: 'withdrawal issues', sentiment: 'negative', notes: 'Anything that prevents/slows transfers of the money out/in: withdrawals/deposits aren\'t possible, the fees aren\'t matching, the balance isn\'t updated, frozen wallets, prolonged system downtime and verification process, etc.' },
  { topic: 'fraud', sentiment: 'negative', notes: 'Anything that implies illegal activity' }
];

const cryptoCustodians = ['Binance', 'Coinbase', 'Kraken', 'Huobi', 'OKEx'];

const tweets = [];

function collectTweets() {
  client.get('search/tweets', { q: 'crypto custodians', count: 100 }, function(error, tweets, response) {
    if (!error) {
      tweets.statuses.forEach(function(tweet) {
        const text = tweet.text;
        const topic = getTopic(text);
        if (topic) {
          const sentiment = getSentiment(text);
          if (sentiment === 'negative') {
            tweets.push({ text, topic, sentiment });
          }
        }
      });
    }
  });
}

function getTopic(text) {
  for (const topic of topics) {
    if (text.includes(topic.topic)) {
      return topic.topic;
    }
  }
  return null;
}

function getSentiment(text) {
  // Implement sentiment analysis using a library like Natural or Sentiment
  // For simplicity, this example uses a basic keyword-based approach
  if (text.includes('bad') || text.includes('negative')) {
    return 'negative';
  } else if (text.includes('good') || text.includes('positive')) {
    return 'positive';
  } else {
    return 'neutral';
  }
}

function saveTweets() {
  const fs = require('fs');
  fs.writeFileSync('tweets.json', JSON.stringify(tweets, null, 2));
}

collectTweets();
saveTweets();