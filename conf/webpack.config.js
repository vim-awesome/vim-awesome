var webpack = require("webpack");

var env = process.env.NODE_ENV;

var plugins;
if (env === "development") {
  plugins = [
    new webpack.DefinePlugin({
      "process.env": {NODE_ENV: JSON.stringify("development")}
    }),
  ];
} else if (env === "production") {
  plugins = [
    new webpack.DefinePlugin({
      "process.env": {NODE_ENV: JSON.stringify("production")}
    }),
    new webpack.optimize.UglifyJsPlugin()
  ];
} else {
  throw new Error("Unexpected NODE_ENV value: " + env);
}

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
  },
  plugins: plugins
};
