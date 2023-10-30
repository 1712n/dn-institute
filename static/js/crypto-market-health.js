const fetchMetricsWithAxios = async () => {
    const options = {
        method: 'GET',
        url: 'https://crypto-market-health.p.rapidapi.com/wash_trading_metrics',
        params: {
            market_id: 'COINBASE-BTC-USDT',
            start: '2023-10-26T10:00:00',
            end: '2023-10-29T10:00:00'
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
    //Here if we want, we can bring the timestamp as labels (feat)
    //const labels = data.map(item => new Date(item.timestamp).toLocaleDateString());

    //washtrading and frontrunning data
    const weight = 10;
    const washTradingData = data.map(item => parseFloat(item.volume_volatility_correlation) * weight);
    const frontRunningData = data.map(item => parseFloat(item.buy_sell_count_ratio) * weight);

    const ctx = document.getElementById('myChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec"],
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
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        min: 0,
                        max: 10
                    }
                }]
            }
        }
    });
}

fetchMetricsWithAxios();
