import axios from 'axios';
import { Chart } from 'chart.js';

const options = {
  method: 'GET',
  url: 'https://crypto-market-health.p.rapidapi.com/wash_trading_metrics',
  params: {
    market_id: 'COINBASE-BTC-USDT',
    start: '2023-10-26T10:00:00',
    end: '2023-10-29T10:00:00'
  },
  headers: {
    'X-RapidAPI-Key': 'e205d3d397mshc39f58ef4f8af91p1104b8jsn6eb1a01d8889',
    'X-RapidAPI-Host': 'crypto-market-health.p.rapidapi.com'
  }
};

async function fetchData() {
  try {
    const response = await axios.request(options);
    const data = response.data; // Assumindo que os dados estão neste formato
    
    // Parsear os dados para o formato aceito pelo Chart.js
    const labels = data.map(item => item.timestamp);
    const washTradingData = data.map(item => item.wash_trading_metric);

    // Obter o contexto do canvas onde o gráfico será renderizado
    const ctx = document.getElementById('chartContainer').getContext('2d');
    
    // Criar o gráfico
    new Chart(ctx, {
      type: 'line', // Tipo de gráfico
      data: {
        labels: labels,
        datasets: [{
          label: 'Wash Trading Metric',
          data: washTradingData,
          borderColor: 'rgba(75, 192, 192, 1)',
          fill: false
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          xAxes: [{
            type: 'time',
            time: {
              unit: 'hour'
            }
          }]
        }
      }
    });
  } catch (error) {
    console.error(error);
  }
}

fetchData();