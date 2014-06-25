// A cache of all categories and their corresponding tags.
var allCategories = null;

/**
 * Fetches all plugin categories from server, caching into a variable.
 * @param {Function} callback Invoked with an array of all categories when
 *     available.
 */
var fetchAllCategories = function(callback) {
  if (allCategories) {
    callback(allCategories);
  } else {
    $.getJSON("/api/categories", function(data) {
      allCategories = data;
      callback(allCategories);
    });
  }
};

module.exports = fetchAllCategories;
