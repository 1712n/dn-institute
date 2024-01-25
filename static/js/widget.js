const options = {
  method: 'GET',
  url: 'https://crypto-market-health.p.rapidapi.com/metrics',
  params: {
    limit: 50,
    sort: 'asc'
  },
  headers: {
    'X-RapidAPI-Key': "3cec989436msh6654c961feb2e1ap1339edjsn7f5bca03d992",
    'X-RapidAPI-Host': "crypto-market-health.p.rapidapi.com"
  }
};
const skipped = (ctx, value) => ctx.p0.skip || ctx.p1.skip ? value : undefined;
const down = (ctx, value) => ctx.p0.parsed.y > ctx.p1.parsed.y ? value : undefined;

// Functions
function paintChart(metric) {
    chart.destroy();
    chart = new Chart(context, displayData[metric.value]);
    chart.options.plugins = {
                title: {
                    display: true,
                    text: 'Market Manipulations Metrics'
                }
    };
    chart.update();
};

function parsePair(pair) {
    let exchange = document.getElementById('exchange').value;
    parseData(exchange, pair.value);
};

function parseExchange(exchange) {
    let pair = document.getElementById('pair').value;
    parseData(exchange.value, pair);
};

function parseData(market, pair) {
    options.params.marketvenueid = market;
    options.params.pairid = pair;

    axios.request(options)
        .then((response) => {
            let metricsData = response.data;
            console.log(metricsData);

            // Process data for different metrics
            displayData.buySellRatio = {
                type: "line",
                options: {
                    elements: {
                        point: {
                            radius: 0
                        }
                    }
                },
                data: {
                    labels: metricsData.map(item => new Date(item.timestamp).toLocaleDateString()),
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
                        },
                    ]
                }
            };

            let vwapData = metricsData.map(item => item.vwap);
            displayData.vwap = {
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
                    labels: metricsData.map(item => new Date(item.timestamp).toLocaleDateString()),
                    datasets: [
                        {
                            label: "VWAP",
                            type: "line",
                            data: vwapData,
                            borderColor: 'rgb(127, 0, 127)',
                            tension: 0.1,
                            yAxisID: 'y2'
                        },
                        {
                            label: "Trade Count",
                            type: "bar",
                            data: metricsData.map(item => item.tradecount),
                            backgroundColor: 'rgb(16, 163, 127)',
                        },
                    ]
                }
            };

            let timesOfTradeData = new Array(60).fill(0);
            let totalTradesCount = 0;
            for(let i = 0; i<timesOfTradeData.length; i++) {
                for(let j = 0; j<metricsData.length;j++) {
                    timesOfTradeData[i] += metricsData[j].timeoftrade.seconds[i];
                    totalTradesCount += metricsData[j].timeoftrade.seconds[i];
                }
            }

            let averageTrades = new Array(60).fill(totalTradesCount / 60);
            
            displayData.timesOfTrade = {
                options: {
                        elements: {
                            point: {
                                radius: 0
                            }
                        },
                        // fill: false,
                        // interaction: {
                        //     intersect: false
                        // },
                        // radius: 0,
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
                            label: "Aggregated Trade Frequencies per Second Over All Records",
                            type: "bar",
                            data: timesOfTradeData,
                            backgroundColor: 'rgb(0, 128, 0)',
                        },
                    ]
                }
            };

            let volumeBins = new Array(100).fill(0);
            for(let i = 0; i<volumeBins.length; i++) {
                for(let j = 0; j<metricsData.length;j++) {
                    volumeBins[i] += metricsData[j].volumedist[i][0] + metricsData[j].volumedist[i][1];
                }
            }

            displayData.volumeDistribution = {
                data: {
                    labels: Array.from(Array(100).keys()),
                    datasets: [
                        {
                            label: "Histogram of Trading Volumes",
                            type: "bar",
                            data: volumeBins,
                            backgroundColor: 'rgb(0, 0, 255)',
                        }
                    ]
                }
            };

            let fddData = new Array(9).fill(0);
            for(let i = 0; i<metricsData.length; i++) {
                for(let j = 0; j<10; j++) {
                    fddData[j] += metricsData[i].firstdigitdist[String(j+1)];
                }
            }

            displayData.firstDigitDistribution = {
                data: {
                    labels: Array.from({length: 9}, (_, i) => i + 1),
                    datasets: [
                        {
                            label: "First Digit Distribution",
                            type: "bar",
                            data: fddData,
                            backgroundColor: 'rgb(255, 165, 0)',
                        }
                    ]
                }
            };


            // displayData = {
            //     benford: data.map(item => item.benfordlawtest),
            //     ratio: data.map(item => item.buysellratio),
            //     vwap: data.map(item => item.vwap),
            //     timestamp: data.map(item => item.timestamp)
            // }

            paintChart({value: 'buySellRatio'});
        });
};

let canvas = window.document.querySelector('canvas');
let context = canvas.getContext('2d');

let chart = new Chart(context, {
        options: {
            plugins: {
                title: {
                    display: true,
                    text: 'Market Manipulations Metrics'
                }
            }
}});

var displayData = {};

  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", parseData('ascendex', 'btc-usdt'), {
      passive: true
    })
  else parseData('ascendex', 'btc-usdt');