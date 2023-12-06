title: "Anomalous trades on Poloniex"
date: 2023-10-26 - 2023-10-27
entities:
  - ZEC
  - WBTC	
  
---


The consistent peaks at around 0.0027 can be visually noticed in the volume distribution diagrams for Poloniex, WBTC - USDT, 2023-10-26 - 2023-10-27. 

{{< figure src="wbtc-usdt_volume_distr.png" caption="Hourly volume distribution, 2023/10/26 10:00 – 2023/10/27 10:00, Poloniex, WBTC - USDT" >}}

The volume distribution mode which characterises the most frequent trade size is consistently concentrated around 0.0027 on Poloniex, whereas the equivalent hourly diagrams of the same metric for Binance and Gateio appear to be more variable.

{{< figure src="wbtc-usdt_mode.png" caption="Hourly volume distribution mode, 2023/10/26 10:00 – 2023/10/27 10:00, WBTC - USDT; Poloniex, Binance, Gateio" >}}

Volume generally increases when there is a price movement, so that market volatility and trading volume are correlated with each other and according to the next graph, there were significant fluctuations of price during the given period of time.

{{< figure src="wbtc-usdt_vwap.png" caption="Hourly volume weighted average price of WBTC to USDT, Poloniex, Binance, Gateio, 2023/10/26 10:00 – 2023/10/27 10:00" >}}

However, weak positive, sometimes weak negative correlation in the graph below shows there is no significant relationship between the two variables, which can indicate the volume was inflated.

{{< figure src="wbtc-usdt_volume_volatility.png" caption="Hourly volume-volatility correlation, 2023/10/26 10:00 – 2023/10/27 10:00, Poloniex, WBTC - USDT" >}}

The similar anomaly in trade sizes was detected for ZEC - USDT.

{{< figure src="zec-usdt_volume_distr.png" caption="Hourly volume distribution, 2023/10/26 10:00 – 2023/10/27 10:00, Poloniex, ZEC - USDT" >}}
{{< figure src="zec-usdt_mode.png" caption="Hourly volume distribution mode, 2023/10/26 10:00 – 2023/10/27 10:00, Poloniex, ZEC - USDT" >}}

The buy/sell ratio fluctuates slightly around the 0.5 mark, which looks suspicious because the proportion of buying to selling activity in the market is mostly volatile. The stability around 0.5 can indicate wash trading when buying and selling are executed by the same entity.

{{< figure src="zec-usdt_buy_sell.png" caption="Hourly buy/sell ratio, 2023/10/26 10:00 – 2023/10/27 10:00, Poloniex, ZEC - USDT" >}}