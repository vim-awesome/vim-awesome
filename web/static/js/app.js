(function() {
'use strict';
/*global window: false */

var TEMPLATE_URL = 'static/partials';

// Declare app level module which depends on filters, and services
window.angular.module('myApp', ['myApp.filters', 'myApp.services', 'myApp.directives', 'myApp.controllers']).
  config(['$routeProvider', function($routeProvider) {
    $routeProvider
      .when('', {templateUrl: TEMPLATE_URL + '/plugins_list.html', controller: 'PluginsList'})
      .when('/view1', {templateUrl: TEMPLATE_URL + '/partial1.html', controller: 'MyCtrl1'})
      .when('/view2', {templateUrl: TEMPLATE_URL + '/partial2.html', controller: 'MyCtrl2'})
      .otherwise({redirectTo: ''});
  }]);

})();
