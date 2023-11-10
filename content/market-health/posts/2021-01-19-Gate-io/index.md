---
title: "Anomalous trades on Gate.io"
date: "2021-01-19"
description: "Recent order size distribution on Gate.io deviates from other markets and contradicts Benford's law."
entities:
  - "Gate.io"
  - LTC
  - EOS
  - DASH
---

On January 19, 2021, spot market trades on Gate.io showed signs of falsified numbers. Below are the distributions of leading, second, and third digits for the size of executed trades as compared to [Benford's law](https://en.wikipedia.org/wiki/Benford%27s_law) expected distributions. Evidence based on Benford's law has been used by [ACFE](https://www.acfe.com/uploadedFiles/Shared_Content/Products/Self-Study_CPE/UsingBenfordsLaw_2018_final_extract.pdf) to discern naturally occurring statistical deviations from fraud.

{{< figure src="gateio-ltc-btc.png" caption="First, second, third digit distribution of executed trade sizes on Gate.io, LTC spot market, Jan 2021." >}}

Gate.io demonstrated a noticeable overuse of certain numbers, possibly indicating non-standard trading activity on the exchange. Order size distribution for various coins deviated from other markets and contradicts Benford's law. Similar anomalous trading patterns have been observed across trading pairs listed on this exchange.

{{< figure src="gateio-eos-btc.png" caption="First, second, third digit distribution of executed trade sizes on Gate.io, EOS spot market, Jan 2021." >}}

{{< figure src="gateio-dash-btc.png" caption="First, second, third digit distribution of executed trade sizes on Gate.io, DASH spot market, Jan 2021." >}}
