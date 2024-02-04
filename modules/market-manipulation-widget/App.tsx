import React, { RefObject } from "react";
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    TimeScale,
    ChartType,
    DefaultDataPoint,
    ChartDataset
} from 'chart.js';
import Zoom from 'chartjs-plugin-zoom';
import 'chartjs-adapter-moment';
import { Line } from 'react-chartjs-2';
import { useRef, useEffect, useState } from "react";
import { DictionaryRequest, MetricsResponse, dictionary, metrics, ApiError } from "./api-client";
import { clean, getTimeLimits } from "./utils";
import moment from 'moment'; 
import { data, options } from './options';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    TimeScale,
    Zoom
);

let metricsData: MetricsResponse[] = [];

let chartRef: ChartJS<ChartType, DefaultDataPoint<ChartType>, unknown> | undefined | null;
let marketvenueSelectRef: HTMLSelectElement | null;
let pairSelectRef: HTMLSelectElement | null;


const fetchMarketVenues = async(pair: string): Promise<string[]> => {
  const response = await dictionary({
    pairid: pair,
    limit: 1000
  });

  return response.map(x => x.marketvenueid);
}

const fetchPairs = async(marketvenueid: string): Promise<string[]> => {
  const response = await dictionary({
    marketvenueid: marketvenueid,
    limit: 1000
  });

  return response.map(x => x.pairid);
}

const updateData = async(pair: string, marketvenue: string) => {
  if (!chartRef) {
    return;
  }

  const labels = chartRef.data.labels;
  if (!labels) return;

  const datasets = chartRef.data.datasets;
  clean(labels, datasets);

  const pieces: MetricsResponse[][] = [];
  const timeLimits = getTimeLimits();
  let currentMin = new Date(new Date().setDate(new Date().getDate() - 1)).valueOf();
  while (currentMin < timeLimits.max - 10*60* 1000) {
    const end = timeLimits.max;
    const data = await metrics({
      marketvenueid: marketvenue, 
      pairid: pair, 
      end: moment(end).format('YYYY-MM-DDTHH:mm:ss'),
      start: moment(new Date(currentMin)).format('YYYY-MM-DDTHH:mm:ss'),
      sort: 'asc' as const, 
      limit: 1000});

    if ('error' in data) {
      break;
    } else {
      pieces.push(data);
      currentMin = Date.parse(data[data.length - 1].timestamp).valueOf();
    }
  }
  metricsData = pieces.reverse().flat();
  
  for (const { timestamp, vwap, tradecount, buysellratio, buysellratioabs } of metricsData) {
      labels?.push(Date.parse(timestamp));
      datasets[0].data.push(vwap);
      datasets[1].data.push(tradecount);
      datasets[2].data.push(buysellratio);
      datasets[3].data.push(buysellratioabs);
  }
  chartRef?.update();
}

export default function App() {
  const [formData, setFormData] = useState({
    marketvenue: 'binance',
    pair: 'btc-usdt',
    marketvenues: ['binance'],
    pairs: ['btc-usdt']
  });

  const updateFormData = async(pair: string | null, marketvenue: string | null, needUpdateData?: boolean) => {
    if (pair && marketvenue) {
      setFormData({
        pair: pair,
        marketvenue: marketvenue,
        marketvenues: await fetchMarketVenues(pair),
        pairs: await fetchPairs(marketvenue)
      });
    } else if (pair) {
      setFormData({
        pair: pair,
        marketvenue: formData.marketvenue,
        marketvenues: await fetchMarketVenues(pair),
        pairs: formData.pairs
      });
    } else if (marketvenue) {
      setFormData({
        pair: formData.pair,
        marketvenue: marketvenue,
        marketvenues: formData.marketvenues,
        pairs: await fetchPairs(marketvenue)
      });
    } else {
      return;
    }

    if (marketvenueSelectRef)
      marketvenueSelectRef.value = marketvenue ?? formData.marketvenue;
    
    if (pairSelectRef)
      pairSelectRef.value = pair ?? formData.pair;

    if (needUpdateData) {
      await updateData(pair ?? formData.pair, marketvenue ?? formData.marketvenue)
    }
  }
  
  const onLoad = async() => {
    if (chartRef && chartRef.config.options && chartRef.config.options.scales) {
      const xAxis = chartRef.config.options.scales['x'];
      if (xAxis) {
          let max = new Date().valueOf();
          let min = new Date(new Date().setDate(new Date().getDate() - 1)).valueOf();
          xAxis.min = min;
          xAxis.max = max;
      }
    }
  
    await Promise.all([
      updateFormData(formData.pair, formData.marketvenue, false),
      updateData(formData.pair, formData.marketvenue)
    ]);
  }


  useEffect(() => {
    (async () => await onLoad())()
  }, []);

  

  const getPairs = () => {
    return formData.pairs.map(x => {
      return <option value={x}>{x.toUpperCase()}</option>
    })
  }
  
  const getMarketVenues = () => {
    return formData.marketvenues.map(x => {
      return <option value={x}>{x.toUpperCase()}</option>
    })
  }
  return (
    <>
      <form>
        <select onChange={async (x) => await updateFormData(null, x.target.value, true)} ref={x => marketvenueSelectRef = x}>
          {getMarketVenues()}
        </select>
        <select onChange={async(x) => await updateFormData(x.target.value, null, true)} ref={x => pairSelectRef = x}>
          {getPairs()}
        </select>
      </form>
      <Line options={options} data={data} ref={(reference) => chartRef = reference} />
    </>
  );
}
