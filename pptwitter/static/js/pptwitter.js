'use strict';


var pptwitter = angular.module('pptwitter', ['ngRoute', 'ui', 'ui.bootstrap']);
pptwitter.config(function($interpolateProvider) {
    $interpolateProvider.startSymbol('((');
    $interpolateProvider.endSymbol('))');
});