
## Overview

The Market Health Reporter is a tool for creating automated reports with interactive charts showing metrics spikes and their interpretation using the Market Health API 🌰.

## Installation


Reports are generated as markdown files in the `content/reports/` directory.

## Dynamic Charts

The reporter now supports dynamic, interactive charts using Chart.js. Use the `market-health-chart` shortcode in your markdown files:

`{{</* market-health-chart metric="volatility" exchange="binance" symbol="BTCUSDT" days="30" */>}}`

## API Usage

The tool uses the Market Health API at `https://dn.institute/market-health/api/`