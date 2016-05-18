"use strict";

var _ = require("lodash");

// Given a search string, find the values that have a given prefix.
function getQueriesWithPrefix(queryString, prefix) {
  function hasPrefix(query) {
    var parts = query.split(":");
    return parts[0] === prefix && parts[1];
  }

  function getValue(query) {
    return query.split(":")[1];
  }

  var queries = queryString.split(" ");
  var queriesWithPrefix = _.filter(queries, hasPrefix);
  return _.map(queriesWithPrefix, getValue);
}

module.exports = {
  getQueriesWithPrefix: getQueriesWithPrefix
}
