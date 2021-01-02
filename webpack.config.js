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
      $: 'jquery',
      jQuery: 'jquery'
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
        exclude: /node_modules|static\/emails\.scss/,
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
        test: /\.(ttf|eot|svg|otf|png|jpeg|jpg|woff|woff2)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        exclude: /node_modules|static\/emails\.scss/,
        use: [{
            loader: 'url-loader',
            options: { 
                limit: 8000, // Convert images < 8kb to base64 strings
                name: 'images/[hash]-[name].[ext]',
                publicPath: './'
            }
        }]
    }
    ]
  }
}

module.exports = config
