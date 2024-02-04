const path = require('path');

module.exports = {
  mode: 'none',
  entry: {
    marketManipulationWidget: path.resolve(__dirname, 'index.tsx')
  },
  target: 'web',
  resolve: {
      extensions: ['.ts', '.tsx', '.js']
  },
  output: {
    path: path.resolve('..', '..', 'static', 'assets'),
    filename: '[name].js',
  },
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        exclude: /node_modules/,
        use: ['ts-loader'],
      },
    ],
  },
};