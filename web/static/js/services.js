(function() {
'use strict';
/*global window: false */

// Demonstrate how to register services
// In this case it is a simple value service.
window.angular.module('myApp.services', ['ngResource'])
  .value('version', '0.1')
  .factory('Plugins', function($resource) {
    // TODO(david): Param defaults (2nd arg)
    return $resource('/api/plugins', {}, {
      query: {
        method:'GET',
        params: {},
        isArray: true
      }
    });
  })
;

})();
