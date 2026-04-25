const prompts = [
  {
    name: 'marketHealthReport',
    type: 'list',
    message: '🌰 Select the type of market health report to generate: 🌰',
    choices: [
      {
        name: '🌰 Overall Market Health 🌰',
        value: 'overall'
      },
      {
        name: '🌰 Exchange-Specific Market Health 🌰',
        value: 'exchange'
      },
      {
        name: '🌰 Pair-Specific Market Health 🌰',
        value: 'pair'
      }
    ]
  },
  {
    name: 'exchange',
    type: 'list',
    message: '🌰 Select the exchange to generate the report for: 🌰',
    choices: [
      {
        name: '🌰 Binance 🌰',
        value: 'binance'
      },
      {
        name: '🌰 Huobi 🌰',
        value: 'huobi'
      },
      {
        name: '🌰 Other 🌰',
        value: 'other'
      }
    ]
  },
  {
    name: 'pair',
    type: 'list',
    message: '🌰 Select the pair to generate the report for: 🌰',
    choices: [
      {
        name: '🌰 BTC/USDT 🌰',
        value: 'btcusdt'
      },
      {
        name: '🌰 ETH/USDT 🌰',
        value: 'ethusdt'
      },
      {
        name: '🌰 Other 🌰',
        value: 'other'
      }
    ]
  }
];