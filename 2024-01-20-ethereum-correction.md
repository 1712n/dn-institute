--- a/tools/market_health_reporter/content/reports/2024-01-20-ethereum-correction.md
+++ b/tools/market_health_reporter/content/reports/2024-01-20-ethereum-correction.md
@@ -8,7 +8,7 @@
 
 ## Price Movement Analysis
 
-![ETH/USD Price Chart](images/eth-usd-price-24h.png)
+{{< metric-chart metric="price" exchange="coinbase" base="ETH" quote="USD" timeframe="24h" >}}
 
 Ethereum experienced a sharp correction in the past 24 hours, declining by 12.3% from $2,650 to $2,320. This represents the largest single-day decline in the past 3 months.
 
@@ -16,7 +16,7 @@
 
 ## Volume Analysis
 
-![ETH/USD Volume Chart](images/eth-usd-volume-24h.png)
+{{< metric-chart metric="volume" exchange="coinbase" base="ETH" quote="USD" timeframe="24h" >}}
 
 Trading volume for ETH/USD surged by 210% during the correction, reaching $15.4 billion. This volume spike is typical during sharp downward movements as panic selling occurs.
 
@@ -24,7 +24,7 @@
 
 ## Volatility Metrics
 
-![ETH/USD Volatility Chart](images/eth-usd-volatility-24h.png)
+{{< metric-chart metric="volatility" exchange="coinbase" base="ETH" quote="USD" timeframe="24h" >}}
 
 The 24-hour volatility for ETH/USD spiked to 8.7%, significantly above the 30-day average of 3.2%. This represents a 172% increase in volatility, indicating extreme market stress.
 
