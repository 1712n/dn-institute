const options = {
  method: 'GET',
  url: 'https://crypto-market-health.p.rapidapi.com/metrics',
  params: {
    limit: 50,
    sort: 'asc'
  },
  headers: {
    'X-RapidAPI-Key': RAPID_KEY,
    'X-RapidAPI-Host': RAPID_HOST
  }
};

// Utility function to format date and time
function formatDateAndTime(timestamp) {
  const date = new Date(timestamp);
  const options = { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' };
  return date.toLocaleString('en-US', options);
}

const displayData = {};

// Initialize chart
const canvas = document.querySelector('canvas');
const context = canvas.getContext('2d');
let chart = new Chart(context, {
  options: {
    plugins: {
      title: {
        display: true,
        text: 'Market Manipulations Metrics'
      }
    }
  }
});

function parseDataFromSelects() {
  const exchange = document.getElementById('exchange').value;
  const pair = document.getElementById('pair').value;
  parseData(exchange, pair);
}

function parseData(market, pair) {
  Object.assign(options.params, { marketvenueid: market, pairid: pair });

  axios.request(options).then(response => {
    const metricsData = response.data;
    processData(metricsData);
    paintChart({value: document.getElementById('metric').value});
  });
}

function processData(metricsData) {
  displayData.buySellRatio = createBuySellRatioData(metricsData);
  displayData.vwap = createVwapData(metricsData);
  displayData.timesOfTrade = createTimesOfTradeData(metricsData);
  displayData.volumeDistribution = createVolumeDistributionData(metricsData);
  displayData.firstDigitDistribution = createFirstDigitDistributionData(metricsData);
}

function paintChart(metricKey) {
  if (chart) chart.destroy();
  chart = new Chart(context, displayData[metricKey.value]);
  chart.options.plugins.title = {
    display: true,
    text: 'Market Manipulations Metrics'
  };
  chart.update();
}

function createBuySellRatioData(metricsData) {
  return {
    type: "line",
    options: {
      elements: {
        point: {
          radius: 0
        }
      }
    },
    data: {
      labels: metricsData.map(item => formatDateAndTime(item.timestamp)),
      datasets: [
        {
          label: "Buy/Sell Ratio",
          data: metricsData.map(item => item.buysellratio),
          borderColor: 'rgb(86, 171, 86)',
          borderWidth: 2,
          tension: 0.1
        },
        {
          label: "Buy/Sell Ratio Absolute",
          data: metricsData.map(item => item.buysellratioabs),
          borderColor: 'rgb(77, 77, 255)',
          borderWidth: 2,
          tension: 0.1
        }
      ]
    }
  };
}

function createVwapData(metricsData) {
  return {
    options: {
      elements: {
        point: {
          radius: 0
        }
      },
      scales: {
        y: {
          stack: 'vwapStack',
          stackWeight: 2
        },
        y2: {
          offset: true,
          stack: 'vwapStack',
          stackWeight: 1
        }
      }
    },
    data: {
      labels: metricsData.map(item => formatDateAndTime(item.timestamp)),
      datasets: [
        {
          label: "VWAP",
          type: "line",
          data: metricsData.map(item => item.vwap),
          borderColor: 'rgb(127, 0, 127)',
          tension: 0.1,
          yAxisID: 'y2'
        },
        {
          label: "Trade Count",
          type: "bar",
          data: metricsData.map(item => item.tradecount),
          backgroundColor: 'rgb(16, 163, 127)',
        }
      ]
    }
  };
}

function createTimesOfTradeData(metricsData) {
  let timesOfTradeData = new Array(60).fill(0);
  let totalTradesCount = 0;
  for (let i = 0; i < timesOfTradeData.length; i++) {
    for (let j = 0; j < metricsData.length; j++) {
      timesOfTradeData[i] += metricsData[j].timeoftrade.seconds[i];
      totalTradesCount += metricsData[j].timeoftrade.seconds[i];
    }
  }
  let averageTrades = new Array(60).fill(totalTradesCount / 60);

  return {
    options: {
      elements: {
        point: {
          radius: 0
        }
      }
    },
    data: {
      labels: Array.from(Array(60).keys()),
      datasets: [
        {
          label: "Average Trades Per Second",
          type: "line",
          data: averageTrades,
          borderColor: 'rgb(255, 11, 11)',
          borderDash: [5, 5],
          tention: 0.1
        },
        {
          label: "Trade Frequencies per Second Aggregated Over the Last 7 Days",
          type: "bar",
          data: timesOfTradeData,
          backgroundColor: 'rgb(0, 128, 0)',
        }
      ]
    }
  };
}

function createVolumeDistributionData(metricsData) {
  let volumeBins = new Array(100).fill(0);
  for (let i = 0; i < volumeBins.length; i++) {
    for (let j = 0; j < metricsData.length; j++) {
      volumeBins[i] += metricsData[j].volumedist[i][1];
    }
  }

  return {
    data: {
      labels: Array.from(Array(100).keys()),
      datasets: [
        {
          label: "Histogram of Trading Volumes Aggregated Over the Last 7 Days",
          type: "bar",
          data: volumeBins,
          backgroundColor: 'rgb(0, 0, 255)',
        }
      ]
    }
  };
}

function createFirstDigitDistributionData(metricsData) {
  let fddData = new Array(9).fill(0);
  let totalFDD = 0;
  for (let i = 0; i < metricsData.length; i++) {
    for (let j = 0; j < 10; j++) {
      let currentData = metricsData[i].firstdigitdist[String(j + 1)];
      if (currentData === undefined) { currentData = 0; }
      fddData[j] += currentData;
      totalFDD += currentData;
    }
  }

  // Expected FDD data calculation
  let expectedFddPercentage = [301, 176, 125, 97, 79, 67, 58, 51, 46];
  let expectedFdd = [];
  for (let i = 0; i < 10; i++) {
    expectedFdd.push((totalFDD * expectedFddPercentage[i]) / 1000);
  }

  return {
    options: {
      elements: {
        point: {
          radius: 0
        }
      },
      scales: {
        y: {
          stacked: true
        }
      }
    },
    data: {
      labels: Array.from({ length: 9 }, (_, i) => i + 1),
      datasets: [
        {
          label: "First Digit Distribution",
          data: fddData,
          type: "bar",
          backgroundColor: 'rgb(255, 165, 0)',
          stack: "Stack 1"
        },
        {
          label: "Expected First Digit Distribution",
          data: expectedFdd,
          type: "bar",
          backgroundColor: 'rgb(68, 147, 245)',
          stack: "Stack 2"
        }
      ]
    }
  };
}

// Initial data load
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => parseData('ascendex', 'btc-usdt'), { passive: true });
} else {
  parseData('ascendex', 'btc-usdt');
}
