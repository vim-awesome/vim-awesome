(function() {
'use strict';
/*global window: false */

// Demonstrate how to register services
// In this case it is a simple value service.
window.angular.module('myApp.services', []).
  value('version', '0.1');

})();
