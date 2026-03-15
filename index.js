const express = require('express');
const axios = require('axios');
const natural = require('natural');

const app = express();
const port = 3000;

const Analyzer = natural.SentimentAnalyzer;
const stemmer = natural.PorterStemmer;
const analyzer = new Analyzer('English', stemmer, 'afinn');

app.get('/analyze', async (req, res) => {
  const { query } = req.query;
  if (!query) {
    return res.status(400).send('Query parameter is required');
  }

  try {
    const response = await axios.get(`https://newsapi.org/v2/everything?q=${query}&apiKey=YOUR_NEWS_API_KEY`);
    const articles = response.data.articles;
    const sentiments = articles.map(article => ({
      title: article.title,
      sentiment: analyzer.getSentiment(article.description.split(' '))
    }));
    res.json(sentiments);
  } catch (error) {
    res.status(500).send('Error fetching data');
  }
});

app.listen(port, () => {
  console.log(`AI Product listening at http://localhost:${port}`);
});