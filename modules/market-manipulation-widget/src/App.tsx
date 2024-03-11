import React from "react"
import { useEffect, useState } from "react"
import ReactApexChart from "react-apexcharts"
import MetricsData from "./models/metricsData"
import updateCharts from "./utils/updateCharts"
import updateForm from "./utils/updateForm"
import State from "./models/state"
import Select from "react-select"
import { VolumeChart, BuySellChart } from ".."

const metricsData: MetricsData = {
  data: []
}

let marketvenueSelectRef: HTMLSelectElement | null
let pairSelectRef: HTMLSelectElement | null

export default function App() {
  const [state, setState] = useState({
    marketvenue: "binance",
    pair: "btc-usdt",
    marketvenues: ["binance"],
    pairs: ["btc-usdt"],
    dataPointIndex: null
  } as State)

  const onLoad = async (
    pair?: string | undefined,
    market?: string | undefined
  ) => {
    const chart1 = ApexCharts.getChartByID("vwap-trade-count")
    if (chart1 === undefined) {
      return
    }
    chart1.resetSeries()
    const chart2 = ApexCharts.getChartByID("buy-sell-ratio")
    if (chart2 === undefined) {
      return
    }
    chart2.resetSeries()

    pair = pair ?? state.pair
    market = market ?? state.marketvenue

    await Promise.all([
      updateForm(pair, market, state, setState),
      updateCharts(chart1, chart2, pair, market, metricsData)
    ])

    if (marketvenueSelectRef) marketvenueSelectRef.value = market
    if (pairSelectRef) pairSelectRef.value = pair
  }

  useEffect(() => {
    ;(async () => await onLoad())()
  }, [])

  const getOptions = (values: string[]) => {
    return values.map((x) => {
      return { value: x, label: x }
    })
  }

  const options3 = {
    title: {
      text: "Volume Distribution",
      align: "center" as const
    },
    chart: {
      id: "volumedist",
      type: "bar" as const
    },
    plotOptions: {
      bar: {
        distributed: true
      }
    },
    dataLabels: {
      enabled: false
    },
    legend: {
      show: false
    },
    xaxis: {
      labels: {
        show: false
      }
    }
  }

  const options4 = {
    title: {
      text: "Time-of-Trade",
      align: "center" as const
    },
    chart: {
      id: "timeoftrade",
      type: "bar" as const
    },
    plotOptions: {
      bar: {
        distributed: true
      }
    },
    dataLabels: {
      enabled: false
    },
    legend: {
      show: false
    },
    xaxis: {
      labels: {
        show: false
      }
    }
  }

  const options5 = {
    title: {
      text: "Benford’s Law",
      align: "center" as const
    },
    chart: {
      id: "firstdigitdist",
      type: "bar" as const
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: "55%",
        endingShape: "rounded"
      }
    },
    dataLabels: {
      enabled: false
    },
    fill: {
      opacity: 1
    },
    stroke: {
      show: true,
      width: 2,
      colors: ["transparent"]
    }
  }

  const selectStyle = {
    container: (styles: object) => ({ ...styles, width: "20rem" }),
    control: (styles: object) => ({ ...styles, width: "20rem" }),
    option: (styles: object) => ({ ...styles, width: "20rem" })
  }

  const updateDataPointIndex = (dataPointIndex: number) => {
    state.dataPointIndex = dataPointIndex
    setState({ ...state })
  }

  return (
    <>
      <form>
        <Select
          options={getOptions(state.marketvenues)}
          defaultValue={{ value: "binance", label: "binance" }}
          onChange={async (x) => await onLoad(undefined, x?.value)}
          styles={selectStyle}
        />
        <Select
          options={getOptions(state.pairs)}
          defaultValue={{ value: "btc-usdt", label: "btc-usdt" }}
          onChange={async (x) => await onLoad(x?.value)}
          styles={selectStyle}
        />
      </form>

      <VolumeChart
        dataPointIndex={state.dataPointIndex}
        metricsData={metricsData}
        updateDataPointIndex={updateDataPointIndex}
        height={200}
      />
      <BuySellChart height={200} />

      {state.dataPointIndex != null && (
        <ReactApexChart options={options3} series={[]} height="250" />
      )}

      {state.dataPointIndex != null && (
        <ReactApexChart options={options4} series={[]} height="250" />
      )}

      {state.dataPointIndex != null && (
        <ReactApexChart options={options5} series={[]} height="250" />
      )}
    </>
  )
}
