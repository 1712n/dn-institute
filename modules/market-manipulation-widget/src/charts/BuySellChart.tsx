import React from "react"
import ReactApexChart from "react-apexcharts"

const options = () => {
  return {
    chart: {
      id: "buy-sell-ratio",
      group: "market-health"
    },
    xaxis: {
      type: "datetime" as const,
      labels: {
        datetimeFormatter: {
          year: "yyyy",
          month: "MMM 'yy",
          day: "dd MMM",
          hour: "HH:mm"
        }
      }
    },
    noData: {
      text: "Loading...",
      align: "center" as const,
      verticalAlign: "middle" as const
    },
    dataLabels: {
      enabled: false
    },
    markers: {
      size: 0
    },
    zoom: {
      type: "x",
      enabled: true,
      autoScaleYaxis: true
    },
    stroke: {
      width: 1
    },
    tooltip: {
      shared: true,
      intersect: false,
      enabled: true,
      x: {
        format: "dd MMM HH:mm"
      }
    }
  }
}

interface ButSellChartProps {
  height: number
}

function BuySellChart(props: ButSellChartProps) {
  return (
    <ReactApexChart
      options={options()}
      series={[]}
      type="line"
      height={props.height}
    />
  )
}

export { BuySellChart, ButSellChartProps }
