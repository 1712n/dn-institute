const options = {
  method: 'GET',
  url: 'https://crypto-market-health.p.rapidapi.com/metrics',
  params: {
    limit: 50,
    sort: 'asc'
  },
  headers: {
    'X-RapidAPI-Key': RAPID_KEY,
    'X-RapidAPI-Host': RAPID_HOST
  }
};

// Utility function to format date and time
function formatDateAndTime(timestamp) {
  const date = new Date(timestamp);
  const options = { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' };
  return date.toLocaleString('en-US', options);
}

const displayData = {};

// Initialize chart
const canvas = document.querySelector('canvas');
const context = canvas.getContext('2d');
let chart = new Chart(context, {
  options: {
    plugins: {
      title: {
        display: true,
        text: 'Market Manipulations Metrics'
      }
    }
  }
});

function parseDataFromSelects() {
  const exchange = document.getElementById('exchange').value;
  const pair = document.getElementById('pair').value;
  parseData(exchange, pair);
}

function parseData(market, pair) {
  fetch(`https://crypto-market-health.p.rapidapi.com/metrics?exchange=${market}&pair=${pair}`, options)
    .then(response => response.json())
    .then(data => {
      displayData[market] = displayData[market] || {};
      displayData[market][pair] = data;
      renderChart(data);
    })
    .catch(error => console.error(error));
}

function renderChart(data) {
  chart.data.labels = data.map(item => formatDateAndTime(item.timestamp));
  chart.data.datasets[0].data = data.map(item => item.value);
  chart.update();
}