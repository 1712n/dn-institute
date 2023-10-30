const chartConfig = {
  type: "line",
  data: {
    labels: [], // Vamos começar com um array vazio e preenchê-lo dinamicamente
    datasets: [
      {
        label: "Wash Trading",
        data: [],
        borderColor: "rgba(75, 192, 192, 1)",
        fill: false,
        pointBackgroundColor: "rgba(75, 192, 192, 1)",
        pointBorderColor: "rgba(75, 192, 192, 1)"
      },
      {
        label: "Front Running",
        data: [],
        borderColor: "rgba(153, 102, 255, 1)",
        fill: false,
        pointBackgroundColor: "rgba(153, 102, 255, 1)",
        pointBorderColor: "rgba(153, 102, 255, 1)"
      }
    ]
  },
  options: {
    responsive: false,
    maintainAspectRatio: false,
    scales: {
      xAxes: [
        {
          type: "category",
          distribution: "linear",
          gridLines: {
            display: false
          },
          ticks: {
            callback: function (value) {
              const date = new Date(value)
              return `${date.getDate()}/${
                date.getMonth() + 1
              }/${date.getFullYear()}`
            }
          }
        }
      ],
      yAxes: [
        {
          ticks: {
            min: -10,
            max: 50,
            stepSize: 10
          }
        }
      ]
    }
  }
}

const ctx = document.getElementById("chartContainer").getContext("2d")
const chart = new Chart(ctx, chartConfig) // Cria o gráfico uma vez

async function fetchData() {
  const apiOptions = {
    method: "GET",
    url: "https://crypto-market-health.p.rapidapi.com/wash_trading_metrics",
    params: {
      market_id: "COINBASE-BTC-USDT",
      start: "2023-10-20T10:00:00",
      end: "2023-10-30T10:00:00"
    },
    headers: {
      "X-RapidAPI-Key": "e205d3d397mshc39f58ef4f8af91p1104b8jsn6eb1a01d8889",
      "X-RapidAPI-Host": "crypto-market-health.p.rapidapi.com"
    }
  }

  //   try {
  //     const response = await axios.request(apiOptions)
  //     const dataArray = response.data.data

  //     chartConfig.data.labels = dataArray.map((item) => new Date(item.timestamp))
  //     chartConfig.data.datasets[0].data = dataArray.map((item) =>
  //       item.first_digit_distribution.reduce((a, b) => a + b, 0)
  //     )

  //     chart.update() // Atualiza o gráfico com os novos dados
  //   } catch (error) {
  //     console.error(error)
  //   }

  try {
    const response = await axios.request(apiOptions)
    const dataArray = response.data.data

    // Formatando as datas para mostrar somente dia e mês
    const formattedDates = dataArray.map((item) => {
      const date = new Date(item.timestamp)
      return date.toLocaleDateString("pt-BR", {
        day: "2-digit",
        month: "2-digit"
      })
    })

    chartConfig.data.labels = formattedDates
    chartConfig.data.datasets[0].data = dataArray.map((item) =>
      item.first_digit_distribution.reduce((a, b) => a + b, 0)
    )

    chart.update() // Atualiza o gráfico com os novos dados
  } catch (error) {
    console.error(error)
  }
}

fetchData()
