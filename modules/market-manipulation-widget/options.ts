import {getTimeLimits} from "./utils";

import {
    Chart as ChartJS
} from 'chart.js';

const zoomOptions = {
    zoom: {
      wheel: {
        enabled: true,
      },
      pinch: {
        enabled: true,
      },
      mode: "x" as const
    },
    pan: {
      enabled: true,
      mode: "x" as const
    },
    limits: {
        x: getTimeLimits()
    }
  };

const options = {
  responsive: true,
  plugins: {
    legend: {
      position: 'top' as const,
    },
    title: {
      display: false,
    },
    zoom: zoomOptions
  },
  scales: {
      x: {
          type: 'time' as const,
          max: new Date().valueOf(),
          min: new Date(new Date().setDate(new Date().getDate() - 7)).valueOf(),
          time: {
            displayFormats: {
              day: 'DD HH:mm',
              hour: 'HH:mm',
              minute: 'HH:mm',
              second: 'HH:mm:ss'
            }
          },
          title: {
              display: false
          }
      }
  }
};



const data = {
    labels: [],
    datasets: [
      {
        label: 'VWAP',
        data: [],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        spanGaps: true
      },
      {
        label: 'Trade count',
        data: [],
        borderColor: 'rgb(53, 162, 100)',
        backgroundColor: 'rgba(53, 162, 100, 0.5)',
        spanGaps: true,
        hidden: true
      },
      {
        label: 'Buy/Sell Ratio',
        data: [],
        borderColor: 'rgb(53, 262, 235)',
        backgroundColor: 'rgba(53, 262, 235, 0.5)',
        spanGaps: true,
        hidden: true
      },
      {
        label: 'Buy/Sell Ratio ABS',
        data: [],
        borderColor: 'rgb(53, 62, 235)',
        backgroundColor: 'rgba(53, 62, 235, 0.5)',
        spanGaps: true,
        hidden: true
      },
    ],
  };

export { options, data };