"use strict"

var ReactTools = require('react-tools');

module.exports = {
  process: function(src, path) {
    if (/\.jsx$/.test(path)) {
      src = ReactTools.transform(src, {harmony: true});
      return src;
    }
    return src;
  }
};
