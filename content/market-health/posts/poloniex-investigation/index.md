title: "Anomalous trades on Poloniex"
date: 2023-10-26 -  2023-10-27
entities:
  - zec
  - wbct	
  
---


Hourly volume distribution mode for WBTC - USDT on Poloniex consistently concentrated around 3 looks suspicious compared to the charts of the same metric for Binance and Gateio.

{{< figure src="wbtc-usdt_mode.png" caption="Hourly volume distribution mode, 2023/10/26 10:00 - 2023/10/27 10:00, WBTC - USDT; Poloniex, Binance, Gateio" >}}

Volume distribution mode characterizes the most frequent trade size, and it can be seen in the figure below that 3 is at the tail of the volume distribution diagram,  which doesn't align with healthy marker behavior where the most frequent trade sizes are small and deviations are random.

{{< figure src="wbtc-usdt_volume_distr.png" caption="Hourly volume distribution, 2023/10/26 10:00 – 2023/10/27 10:00, Poloniex, WBTC - USDT" >}}

Normally, trading volume and market volatility are correlated with each other, volume increases when volatility rises and vice versa. On the contrary, there is no strong connection between these two metrics for WBTC - USDT in the specified period of time. Values lower than 0.4 sometimes negative are observed, which is considered as a signal of market manipulation.

{{< figure src="wbtc-usdt_volume_volatility.png" caption="Hourly volume-volatility correlation, 2023/10/26 10:00 – 2023/10/27 10:00, Poloniex, WBTC - USDT" >}}

The similar pattern was detected for ZEC - USDT.

{{< figure src="zec-usdt_volume_distr.png" caption="Hourly volume distribution, 2023/10/26 10:00 – 2023/10/27 10:00, Poloniex, ZEC - USDT" >}}

Buy/sell ratio here is relatively stable around 0.5. This metric is usually volatile, whereas the consistency around 0.5 can indicate wash trading when buying and selling are executed by the same entity.

{{< figure src="zec-usdt_buy_sell.png" caption="Hourly buy/sell ratio, 2023/10/26 10:00 – 2023/10/27 10:00, Poloniex, ZEC - USDT" >}}