import Chart from 'chart.js/auto';

const chartElement = document.getElementById('marketHealthChart');

const data = {
  labels: ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'],
  datasets: [
    {
      label: 'Wash Trading',
      data: [5, 8, 10, 12, 15, 18, 20, 22, 25, 28, 30, 32],
      borderColor: 'blue',
      fill: false,
    },
    {
      label: 'Front Running',
      data: [10, 15, 12, 8, 20, 25, 30, 22, 18, 14, 10, 8],
      borderColor: 'red',
      fill: false,
    },
  ],
};

const chart = new Chart(chartElement, {
  type: 'line',
  data: data,
  options: {
    scales: {
      y: {
        beginAtZero: true,
        suggestedMin: -10,
        suggestedMax: 50,
      },
    },
  },
});

export default chart;