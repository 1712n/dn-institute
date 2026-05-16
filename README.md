Distributed Networks Institute (DNI) aims to help infrastructure resilience and financial health of distributed networks through scientific, engineering, and educational efforts. We are a part of a 501(c)3 non-profit incubator in Washington, DC called [BlockShop](https://blockshop.org/). Constantly on the lookout for talent, we encourage anyone to contribute code, market analysis, and engineering expertise to one of our [active projects](https://dn.institute/#projects). Multiple research grants and [code bounties](https://github.com/1712n/dn-institute/labels/%F0%9F%92%B0%20bounty) are available.

## 🏆 Challenge Program

[![Challenge Program Video](https://blockshopdc.com/static/assets/images/challenge.jpg)](https://link.hygge.work/MayaVick_Challenge)

We maintain a list of real-world problems we work on to give interested individuals a chance to prove themselves, learn a bit about us, and boost their GitHub profiles in the process. The challenge program was so successful for some teams, that they made solving a challenge a hard requirement for joining them. Our challenges are extremely independent and will require you to manage your own time and work process. Check out the [success stories](https://www.instagram.com/explore/tags/challenge_successstory/) of the challenge winners.

### General rules

- Anyone can participate in a challenge. You do not need anyone's approval to start working or to submit your results.
- Some challenges are paid and have bounties attached to them. When you complete a bounty task, please message bounty-payout@dn.institute with a link to your merged pull request and a Bitcoin or an altcoin address to get paid. We pay all bounties at the end of each month and close tasks as soon as we get enough good quality submissions that fulfill all the requirements.
- By participating in the Challenge Program, you agree to let challenge creators use any and all work submitted for any internal or external purposes.

### Navigating and Working with the Tasks

- In the [issue list](https://github.com/1712n/dn-institute/issues), you'll find a list of tasks that are currently available.
- You are free to start working on any open challenge issue whenever you want.
- For highly complex tasks, we are willing to lock individual issues for qualified candidates to make sure no one else is working on it. For that, please comment in the issue and email challenge@blockshop.org with your CV/profile. We'll review your request and assign the issue exclusively to you.
- To be alerted whenever we create new tasks, please click "👁 Watch" and "☆ Star" in the upper right corner.

## 🌱 Giving Back

### 🔬 Research

DNI has a growing scientific research team, focused on the application of Large Language Models to risk modeling. If you are interested in gaining relevant skills while publishing scientific papers along the way, solve one of the [NLP challenges](https://github.com/1712n/dn-institute/labels/nlp) and mention your interest in joining the research team. Multiple research grants are available!

### 🧑‍🎓 Training

We are happy to train anyone willing to learn our tools. Show initiative by contributing to one of the [open issues](https://github.com/1712n/dn-institute/issues) and mention in your pull request that you want to be considered for any training opportunities they might have available.

### 🎖️ Veterans

Our diverse community includes military veterans from a wide variety of backgrounds. If you are in the process of getting out of the U.S. military, check out our SkillBridge program. Whether you qualify as eligible U.S. military personnel, or served in the armed forces of another country, solve one of the challenges and/or reach out to [@jhirschkorn](https://github.com/jhirschkorn).

## 📊 Detecting Wash Trading with Python: A Practical Guide

Wash trading is a form of market manipulation where traders buy and sell assets to create false market activity, often to inflate trading volume or manipulate price. Detecting such patterns is crucial for maintaining market integrity, and Python provides powerful tools for analyzing and visualizing this data. In this section, we'll walk through a practical example of how to detect wash trading using the DNI API and Python.

First, let's fetch the relevant data from the DNI API. The API provides metrics such as `wash_trading_volume` and `orderbook_imbalance`, which are essential for identifying suspicious trading behavior.

```python
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Replace with your API key
API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.dn.institute/market-health"

# Fetch wash trading data
response = requests.get(f"{BASE_URL}/wash-trading", headers={"Authorization": f"Bearer {API_KEY}"})
data = response.json()

# Convert to DataFrame
df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)
```

Once we have the data, we can visualize it to identify any unusual patterns. For instance, a sudden spike in `wash_trading_volume` could indicate a wash trade.

```python
plt.figure(figsize=(14, 7))
plt.plot(df.index, df['wash_trading_volume'], label='Wash Trading Volume')
plt.title('Wash Trading Volume Over Time 🌟')
plt.xlabel('Time')
plt.ylabel('Volume')
plt.legend()
plt.grid(True)
plt.show()
```

Next, we can analyze the `orderbook_imbalance` metric to detect any anomalies. A high imbalance might suggest that a large number of orders are being placed on one side of the book, which is a common indicator of wash trading.

```python
plt.figure(figsize=(14, 7))
plt.plot(df.index, df['orderbook_imbalance'], label='Orderbook Imbalance')
plt.title('Orderbook Imbalance Over Time 📈')
plt.xlabel('Time')
plt.ylabel('Imbalance')
plt.legend()
plt.grid(True)
plt.show()
```

To further refine our analysis, we can calculate rolling averages and standard deviations to detect deviations from normal behavior.

```python
df['wash_volume_rolling_mean'] = df['wash_trading_volume'].rolling(window=7).mean()
df['wash_volume_rolling_std'] = df['wash_trading_volume'].rolling(window=7).std()

plt.figure(figsize=(14, 7))
plt.plot(df.index, df['wash_trading_volume'], label='Wash Trading Volume')
plt.plot(df.index, df['wash_volume_rolling_mean'], label='7-Day Rolling Mean')
plt.fill_between(df.index, df['wash_volume_rolling_mean'] - df['wash_volume_rolling_std'],
                 df['wash_volume_rolling_mean'] + df['wash_volume_rolling_std'], alpha=0.2, label='7-Day Rolling Std')
plt.title('Wash Trading Volume with Rolling Statistics 📊')
plt.xlabel('Time')
plt.ylabel('Volume')
plt.legend()
plt.grid(True)
plt.show()
```

These visualizations and statistical analyses can help identify potential wash trading activities. By leveraging Python and the DNI API, contributors can provide valuable insights into market health and help maintain transparency in the crypto space. 🌟
