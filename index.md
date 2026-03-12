
# DN Institute

## 🌰 AI Market Intelligence Dashboard

Welcome to our AI-powered market intelligence platform. We leverage advanced machine learning models to analyze cryptocurrency market sentiment, identify emerging trends, and provide actionable insights for digital asset investors.

[View Latest Market Intelligence →](/market-intelligence/)

## Latest Research

{% for post in site.research limit:3 %}
{% endfor %}

[View all research →](/research/)

## Latest Market Intelligence 🌰

{% for intel in site.market-intelligence limit:3 %}
  <h3><a href="{{ intel.url }}">{{ intel.title }}</a></h3>
  <p>{{ intel.excerpt | strip_html | truncatewords: 30 }}</p>
  <p><strong>Sentiment:</strong> {{ intel.sentiment_score }}/100 | <strong>Risk:</strong> {{ intel.risk_level }}</p>
{% endfor %}