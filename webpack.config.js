const path = require('path')
const MiniCssExtractPlugin = require('mini-css-extract-plugin')

const config = {
  entry: [
    '/static/js/main.js',
    '/static/scss/main.scss'
  ],
  output: {
    path: path.resolve(__dirname, 'static/dist'),
    filename: 'main.bundle.js'
  },
  externals: {
    jquery: 'jQuery'
  },
  plugins: [
    require('tailwindcss'),
    require('precss'),
    require('autoprefixer'),
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
      }
    ]
  }
}

module.exports = config
