(function() {
'use strict';
/*global window: false */

window.angular.module('myApp.controllers', []).
  controller('MyCtrl1', [function() {

  }])
  .controller('MyCtrl2', [function() {

  }])

  // Controller for the main plugins list view
  .controller('PluginsList', ['$scope', 'Plugins', function($scope, Plugins) {
    $scope.plugins = Plugins.query();

    $scope.sortOptions = {};
    $scope.sortOptions.orderProp = 'name';  // TODO(david): Change to # stars
  }])

  // Main single-page app controller
  .controller('AppController', [function() {
  }])
;

})();
