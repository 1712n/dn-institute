import React from "react"
import ReactApexChart from "react-apexcharts"
import { handleClick } from "../handleClick"
import MetricsData from "../models/metricsData"

const options = (
  dataPointIndex: number | null,
  metricsData: MetricsData,
  updateDataPointIndex: (value: number) => void
) => {
  return {
    chart: {
      id: "vwap-trade-count",
      group: "market-health",
      events: {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        click: (event: object, context: object, config: any) => {
          if (
            config.dataPointIndex === -1 ||
            dataPointIndex === config.dataPointIndex
          ) {
            return
          }

          updateDataPointIndex(config.dataPointIndex)
          handleClick(config.dataPointIndex, metricsData)
        }
      }
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

interface VolumeChartProps {
  dataPointIndex: number | null
  metricsData: MetricsData
  updateDataPointIndex: (value: number) => void
  height: number
}

function VolumeChart(props: VolumeChartProps) {
  return (
    <ReactApexChart
      options={options(
        props.dataPointIndex,
        props.metricsData,
        props.updateDataPointIndex
      )}
      series={[]}
      type="line"
      height={props.height}
    />
  )
}

export { VolumeChartProps, VolumeChart }
