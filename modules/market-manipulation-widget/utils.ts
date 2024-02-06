import { ChartDataset } from "chart.js";


const getTimeLimits = () => {
    return {
      min: new Date(new Date().setDate(new Date().getDate() - 7)).valueOf(),
      max: new Date().valueOf()
    }
  };



const clean = (labels: unknown[], datasets: ChartDataset[]) => {
  while(labels && labels.length > 0) {
    labels?.pop();
  }
  datasets.forEach(dataset => {
    while(dataset.data.length && dataset.data.length > 0) {
      dataset.data.pop();
    }
  });
}

export { getTimeLimits, clean };