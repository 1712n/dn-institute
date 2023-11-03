const chartConfig = {
    type: 'line',
    data: {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        datasets: [{
            label: 'Wash Trading',
            data: [], 
            borderColor: 'rgba(75, 192, 192, 1)',
            fill: false,
            pointBackgroundColor: 'rgba(75, 192, 192, 1)',
            pointBorderColor: 'rgba(75, 192, 192, 1)'
        },
        {
            label: 'Front Running',
            data: [],
            borderColor: 'rgba(153, 102, 255, 1)',
            fill: false,
            pointBackgroundColor: 'rgba(153, 102, 255, 1)',
            pointBorderColor: 'rgba(153, 102, 255, 1)'
        }]
    },
    options: {
        responsive: false,
        maintainAspectRatio: false,
        scales: {
            xAxes: [{
                type: 'category',
                distribution: 'linear',
                gridLines: {
                    display: false
                }
            }],
            yAxes: [{
                ticks: {
                    min: -10,
                    max: 50,
                    stepSize: 10
                }
            }]
        }
    }
  };
  
  const ctx = document.getElementById("chartContainer").getContext("2d")
  const chart = new Chart(ctx, chartConfig) 
  
  async function fetchData() {
      const RAPIDAPIHOST = process.env.RAPIDAPIHOST 
      const  SECRETRAPIDAPI= process.env.SECRETRAPIDAPI
      const apiOptions = {
          method: "GET",
          url: "https://crypto-market-health.p.rapidapi.com/wash_trading_metrics",
          params: {
              market_id: document.getElementById("cryptoSelect").value,
              start: `${document.getElementById("startDate").value}T10:00:00`,
              end: `${document.getElementById("endDate").value}T10:00:00`
          },
          headers: {
              "X-RapidAPI-Key": SECRETRAPIDAPI,
              "X-RapidAPI-Host": RAPIDAPIHOST
          }
      };
      
      try {
          const response = await axios.request(apiOptions);
          const { washTradingData, frontRunningData, labels } = extractDataFromResponse(response);
          
          chartConfig.data.labels = labels;
          chartConfig.data.datasets[0].data = washTradingData;
          chartConfig.data.datasets[1].data = frontRunningData;
          
          chart.update();
      } catch (error) {
          console.error(error);
      }
  }
  
  function extractDataFromResponse(response) {
      const data = response.data.data;
      return {
          washTradingData: data.map(item => parseFloat(item.volume_volatility_correlation)),
          frontRunningData: data.map(item => parseFloat(item.buy_sell_count_ratio)),        
          labels: data.map(item => new Date(item.timestamp).toLocaleDateString())
      };
  }
  
  async function loadAltcoins() {
      try {
          const response = await axios.get("https://api.pro.coinbase.com/products");
          const altcoins = response.data.filter(coin => coin.base_currency).map(coin => coin.base_currency);
          
          populateDropdown(altcoins);
      } catch (error) {
          console.error("Error retrieving altcoins:", error);
      }
  }
  
  function populateDropdown(altcoins) {
      const selectElement = document.getElementById("cryptoSelect");
      selectElement.innerHTML = ""; 
  
      altcoins.forEach(coin => {
          const optionElement = document.createElement("option");
          optionElement.value = `COINBASE-${coin}-USDT`;
          optionElement.textContent = coin;
          selectElement.appendChild(optionElement);
      });
  }
  
  fetchData();
  loadAltcoins();