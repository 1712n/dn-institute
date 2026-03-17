const axios = require('axios');
const natural = require('natural');

const Analyzer = natural.SentimentAnalyzer;
const stemmer = natural.PorterStemmer;
const analyzer = new Analyzer('English', stemmer, 'afinn');

async function fetchNews() {
  try {
    const response = await axios.get('https://newsapi.org/v2/top-headlines?country=us&apiKey=YOUR_API_KEY');
    return response.data.articles;
  } catch (error) {
    console.error('Error fetching news:', error);
    return [];
  }
}

async function analyzeSentiment() {
  const articles = await fetchNews();
  articles.forEach(article => {
    console.log(`Title: ${article.title}`);
    console.log(`Sentiment Score: ${analyzer.getSentiment(article.description)}`);
    console.log('---');
  });
}

analyzeSentiment();