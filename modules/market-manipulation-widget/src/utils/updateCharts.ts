import moment from "moment"
import { metrics } from "../api-client"
import MetricsData from "../models/metricsData"
import DataPoint from "../models/datapoint"

export default async function updateCharts(
  chart1: ApexCharts,
  chart2: ApexCharts,
  pair: string,
  marketvenue: string,
  metricsData: MetricsData
) {
  chart1.resetSeries()

  const timeLimits = moment().utc().valueOf()
  const currentMin = moment().subtract(1, "d").utc().valueOf()

  const end = timeLimits
  const data = await metrics({
    marketvenueid: marketvenue,
    pairid: pair,
    end: moment(end).utc().format("YYYY-MM-DDTHH:mm:ss"),
    start: moment(currentMin).utc().format("YYYY-MM-DDTHH:mm:ss"),
    sort: "asc" as const,
    limit: 1000
  })
  if ("error" in data) {
    throw "dfasdf"
  }
  metricsData.data = data.reverse()

  const vwap: DataPoint[] = []
  const tradeCount: DataPoint[] = []
  const buysellratio: DataPoint[] = []
  const buysellratioabs: DataPoint[] = []
  const yMinMax = [
    {
      min: metricsData.data[0].vwap,
      max: metricsData.data[0].vwap
    },
    {
      min: metricsData.data[0].tradecount,
      max: metricsData.data[0].tradecount
    }
  ]
  metricsData.data.forEach((el) => {
    if (yMinMax[0].min > el.vwap) {
      yMinMax[0].min = el.vwap
    }
    if (yMinMax[0].max < el.vwap) {
      yMinMax[0].max = el.vwap
    }
    if (yMinMax[1].min > el.tradecount) {
      yMinMax[1].min = el.tradecount
    }
    if (yMinMax[1].max < el.tradecount) {
      yMinMax[1].max = el.tradecount
    }

    vwap.push({
      x: el.timestamp,
      y: el.vwap
    })
    tradeCount.push({
      x: el.timestamp,
      y: el.tradecount
    })
    buysellratio.push({
      x: el.timestamp,
      y: el.buysellratio
    })
    buysellratioabs.push({
      x: el.timestamp,
      y: el.buysellratioabs
    })
  })

  chart1.updateOptions(
    {
      series: [
        {
          name: "VWAP",
          type: "line",
          data: vwap
        },
        {
          name: "Trades count",
          type: "line",
          data: tradeCount
        }
      ],
      yaxis: [
        {
          name: "VWAP",
          min: yMinMax[0].min,
          max: yMinMax[0].max,
          axisTicks: {
            show: true
          },
          axisBorder: {
            show: true,
            color: "#008FFB"
          },
          labels: {
            minWidth: 40,
            style: {
              colors: "#008FFB"
            }
          },
          title: {
            text: "VWAP",
            style: {
              color: "#008FFB"
            }
          }
        },
        {
          seriesName: "Trades count",
          opposite: true,
          min: yMinMax[1].min,
          max: yMinMax[1].max,
          axisTicks: {
            show: true
          },
          axisBorder: {
            show: true,
            color: "#00E396"
          },
          labels: {
            minWidth: 40,
            style: {
              colors: "#00E396"
            }
          },
          title: {
            text: "Trades count",
            style: {
              color: "#00E396"
            }
          }
        }
      ]
    },
    false,
    false,
    false
  )

  chart2.updateOptions(
    {
      series: [
        {
          name: "Buy/Sell Ratio",
          type: "line",
          data: buysellratio
        },
        {
          name: "Buy/Sell Ratio Abs",
          type: "line",
          data: buysellratioabs
        }
      ],
      yaxis: [
        {
          name: "Buy/Sell Ratio",
          min: 0,
          max: 1,
          axisTicks: {
            show: true
          },
          axisBorder: {
            show: true,
            color: "#008FFB"
          },
          labels: {
            minWidth: 40,
            style: {
              colors: "#008FFB"
            }
          },
          title: {
            text: "Buy/Sell Ratio",
            style: {
              color: "#008FFB"
            }
          }
        },
        {
          seriesName: "Buy/Sell Ratio Abs",
          opposite: true,
          min: 0,
          max: 1,
          axisTicks: {
            show: true
          },
          axisBorder: {
            show: true,
            color: "#00E396"
          },
          labels: {
            minWidth: 40,
            style: {
              colors: "#00E396"
            }
          },
          title: {
            text: "Buy/Sell Ratio Abs",
            style: {
              color: "#00E396"
            }
          }
        }
      ]
    },
    false,
    false,
    false
  )
}
