module.exports = {
  entry: "./web/static/js/app.jsx",
  output: {
    path: "./web/static/build/js",
    filename: "app.js"
  },
  module: {
    loaders: [
      { test: /\.jsx$/, loader: "jsx-loader?harmony" }
    ]
  }
};
