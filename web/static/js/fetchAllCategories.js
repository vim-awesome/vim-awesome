"use strict";

var $ = require("jquery");

var allCategoriesP = null;

/**
 * Fetches all plugin categories from server, caching into a variable.
 * @param {Function} callback Invoked with an array of all categories when
 *     available.
 */
var fetchAllCategories = function(callback) {
  if (!allCategoriesP) {
    allCategoriesP = $.getJSON("/api/categories");
    // TODO(alpert): Handle errors?
  }
  allCategoriesP.done(callback);
};

module.exports = fetchAllCategories;
