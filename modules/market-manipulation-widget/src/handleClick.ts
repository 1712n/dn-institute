import { MetricsResponse } from "./api-client"
import DataPoint from "./models/datapoint"
import MetricsData from "./models/metricsData"

function updateVolumeDistribution(metric: MetricsResponse, data: DataPoint[]) {
  const chart = ApexCharts.getChartByID("volumedist")
  if (chart === undefined) {
    return
  }
  chart.resetSeries()
  metric.volumedist.forEach((el) => {
    data.push({ x: `${el[0]}`, y: el[1] })
  })
  chart.updateSeries([
    {
      name: "Trades",
      type: "bar" as const,
      data: data
    }
  ])
}

function updateTimeOfTrade(metric: MetricsResponse, data: DataPoint[]) {
  const chart = ApexCharts.getChartByID("timeoftrade")
  if (chart === undefined) {
    return
  }
  chart.resetSeries()
  const seconds = metric.timeoftrade.seconds
  seconds.forEach((el, idx) => {
    data.push({ x: `${idx}`, y: el })
  })
  const avg_count =
    seconds.reduce((acc, v) => {
      return acc + v
    }, 0) / 60
  chart.updateOptions({
    series: [
      {
        name: "Trades",
        type: "bar" as const,
        data: data
      }
    ],
    annotations: {
      yaxis: [
        {
          y: avg_count,
          borderColor: "#00E396",
          label: {
            borderColor: "#00E396",
            style: {
              color: "#fff",
              background: "#00E396"
            },
            text: "Average Trades per Second"
          }
        }
      ]
    }
  })
}

function updateFirstDigitDistribution(
  metric: MetricsResponse,
  firstdigitdist: DataPoint[],
  benfordexpected: DataPoint[]
) {
  const chart = ApexCharts.getChartByID("firstdigitdist")
  if (chart === undefined) {
    return
  }
  chart.resetSeries()
  const data2 = metric.firstdigitdist
  const tradecount = metric.tradecount
  Array.from(Array(9).keys())
    .map((v, i) => i + 1)
    .forEach((el) => {
      const x = `${el}`
      firstdigitdist.push({ x: x, y: data2[el] })
      benfordexpected.push({
        x: x,
        y: Math.round(Math.log10(1 + 1 / el) * tradecount * 100) / 100
      })
    })
  chart.updateOptions({
    series: [
      {
        name: "Observed",
        type: "bar" as const,
        data: firstdigitdist
      },
      {
        name: "Expected (Benford’s Law)",
        type: "bar" as const,
        data: benfordexpected
      }
    ]
  })
}

export function handleClick(dataPointIndex: number, metricsData: MetricsData) {
  if (metricsData.data.length === 0) return

  const volumedist: DataPoint[] = []
  const timeoftrade: DataPoint[] = []
  const firstdigitdist: DataPoint[] = []
  const benfordexpected: DataPoint[] = []

  const metric = metricsData.data[dataPointIndex]

  updateVolumeDistribution(metric, volumedist)
  updateTimeOfTrade(metric, timeoftrade)
  updateFirstDigitDistribution(metric, firstdigitdist, benfordexpected)
}
