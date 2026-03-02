--- a/tools/market_health_reporter/content/reports/2024-01-15-bitcoin-spike.md
+++ b/tools/market_health_reporter/content/reports/2024-01-15-bitcoin-spike.md
@@ -8,7 +8,7 @@
 
 ## Price Movement Analysis
 
-![BTC/USD Price Chart](images/btc-usd-price-24h.png)
+{{< metric-chart metric="price" exchange="binance" base="BTC" quote="USD" timeframe="24h" >}}
 
 Bitcoin experienced a significant price movement in the past 24 hours, with the price increasing by 8.5% from $42,300 to $45,900. This movement was accompanied by above-average trading volume, indicating strong market participation.
 
@@ -16,7 +16,7 @@
 
 ## Volume Analysis
 
-![BTC/USD Volume Chart](images/btc-usd-volume-24h.png)
+{{< metric-chart metric="volume" exchange="binance" base="BTC" quote="USD" timeframe="24h" >}}
 
 Trading volume for BTC/USD increased by 156% compared to the previous 24-hour period, reaching $28.7 billion. This volume spike coincided with the price increase, suggesting genuine buying interest rather than a short squeeze.
 
@@ -24,7 +24,7 @@
 
 ## Volatility Metrics
 
-![BTC/USD Volatility Chart](images/btc-usd-volatility-24h.png)
+{{< metric-chart metric="volatility" exchange="binance" base="BTC" quote="USD" timeframe="24h" >}}
 
 The 24-hour volatility for BTC/USD increased to 4.2%, up from the 30-day average of 2.8%. This represents a 50% increase in volatility, which is significant but not extreme by Bitcoin's historical standards.
 
