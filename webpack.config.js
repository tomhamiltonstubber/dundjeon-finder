const path = require('path')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')
const webpack = require("webpack");


const config = {
  entry: [
    '/static/js/main.js',
    '/static/scss/main.scss'
  ],
  output: {
    path: path.resolve(__dirname, 'static/dist'),
    filename: 'main.bundle.js'
  },
  plugins: [
    require('tailwindcss'),
    require('precss'),
    require('autoprefixer'),
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery"
    }),
    new MiniCssExtractPlugin({filename: '[name].css'}),
  ],
  module: {
    rules: [
      {
        test: /\.(js)$/,
        exclude: /node_modules/,
        use: ['babel-loader']
      },
      {
        test: /\.s[ac]ss$/i,
        exclude: /node_modules/,
        use: [
          MiniCssExtractPlugin.loader,
          {loader: 'css-loader', options: {importLoaders: 1}},
          {loader: 'postcss-loader'},
          {loader: 'sass-loader'}
        ]
      },
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          {loader: 'css-loader', options: {importLoaders: 1}},
          {loader: 'postcss-loader'}
        ]
      },
      {
        test: /\.njk/,
        use: {loader: 'nunjucks-loader'}
      },
      {
       test: /\.(jpe?g|png|gif|woff|woff2|eot|ttf|svg)(\?[a-z0-9=.]+)?$/,
        use: { loader: 'url-loader?limit=100000' }
      }
    ]
  }
}

module.exports = config
