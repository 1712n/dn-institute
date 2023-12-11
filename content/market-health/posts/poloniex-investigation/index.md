title: "Anomalous trades on Poloniex"
date: 2023-10-26 - 2023-10-27
entities:
  - ZEC
  - WBTC	
  
---


The consistent peaks at around 0.0027 can be visually noticed in the volume distribution diagrams for Poloniex, WBTC - USDT, 2023-10-26 - 2023-10-27. 

{{< figure src="wbtc-usdt_volume_distr.png" caption="Hourly volume distribution, 2023/10/26 10:00 – 2023/10/27 10:00, Poloniex, WBTC - USDT" >}}

Here an hourly interval (0, maximum trade size] is divided into 100 equal segments, so that hourly volume distribution diagrams have 100 bars, and an hourly volume distribution mode highlights a segment that contains the largest number of trades.
Hourly volume distribution mode for Poloniex, WBTC - USDT is consistently concentrated around 0.0027, which rises suspicion because the variety of trade sizes on cryptocurrency exchanges is huge. For example, the value of the same metric on the equivalent hourly diagrams for Binance and Gateio sometimes appears repeatedly at around certain marks, since segments containing small values or round values (like $100) are more frequent, but it is never steady.

{{< figure src="wbtc-usdt_mode.png" caption="Hourly volume distribution mode, 2023/10/26 10:00 – 2023/10/27 10:00, WBTC - USDT; Poloniex, Binance, Gateio" >}}

The anomaly in trade sizes was also detected for ZEC - USDT.

{{< figure src="zec-usdt_volume_distr.png" caption="Hourly volume distribution, 2023/10/26 10:00 – 2023/10/27 10:00, Poloniex, ZEC - USDT" >}}
{{< figure src="zec-usdt_mode.png" caption="Hourly volume distribution mode, 2023/10/26 10:00 – 2023/10/27 10:00, Poloniex, ZEC - USDT" >}}

The buy/sell ratio fluctuates slightly around the 0.5 mark, which looks suspicious because the proportion of buying to selling activity in the market is mostly volatile. The stability around 0.5 can indicate wash trading when buying and selling are executed by the same entity.

{{< figure src="zec-usdt_buy_sell.png" caption="Hourly buy/sell ratio, 2023/10/26 10:00 – 2023/10/27 10:00, Poloniex, ZEC - USDT" >}}