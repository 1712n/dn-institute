const fetchMetricsWithAxios = async () => {
    //One week ago date
    const oneWeekAgo = new Date();
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
    const startDate = `${oneWeekAgo.toISOString().split('.')[0]}`;    

    const options = {
        method: 'GET',
        url: 'https://crypto-market-health.p.rapidapi.com/wash_trading_metrics',
        params: {
            market_id: 'COINBASE-BTC-USDT',
            start: startDate
          },
        headers: {
            'X-RapidAPI-Key': '71b34313e5msh56f2aef6d2d2fdap11c943jsn6079f407a0d9',
            'X-RapidAPI-Host': 'crypto-market-health.p.rapidapi.com'
        }
    };

    try {
        const response = await axios(options);
        updateChart(response.data.data);
    } catch (error) {
        console.error(error);
    }
}

const updateChart = (data) => {
    const labels = data.map(item => new Date(item.timestamp).toLocaleDateString());
    const washTradingData = data.map(item => parseFloat(item.count_time_distribution));
    const frontRunningData = data.map(item => parseFloat(item.vwap));


    // Assuming you're using Chart.js, update the chart like so:
    const ctx = document.getElementById('myChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Wash Trading',
                data: washTradingData,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'blue',
                borderWidth: 1,
                fill: false
            },
            {
                label: 'Front Running',
                data: frontRunningData,
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                borderColor: 'red',
                borderWidth: 1,
                fill: false
            }]
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    }
                }]
            }
        }
    });
}

fetchMetricsWithAxios();
