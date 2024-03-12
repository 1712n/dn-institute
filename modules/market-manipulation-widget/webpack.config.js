/* eslint-disable @typescript-eslint/no-var-requires */
/* eslint-disable no-undef */
const path = require("path")
const webpack = require("webpack")
const ESLintPlugin = require("eslint-webpack-plugin")

module.exports = {
  mode: "none",
  entry: {
    marketManipulationWidget: path.resolve(__dirname, "./src/index.tsx")
  },
  target: "web",
  resolve: {
    extensions: [".ts", ".tsx", ".js"]
  },
  output: {
    path: path.resolve("..", "..", "static", "assets"),
    filename: "[name].js"
  },
  plugins: [
    new webpack.DefinePlugin({
      RAPID_HOST: JSON.stringify(process.env.RAPID_HOST),
      RAPID_KEY: JSON.stringify(process.env.RAPID_KEY)
    }),
    new ESLintPlugin()
  ],
  module: {
    rules: [
      {
        test: /\.tsx?$/,
        exclude: /node_modules/,
        use: ["ts-loader"]
      }
    ]
  }
}
