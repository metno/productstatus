"use strict";

var modelstatusApp = angular.module('modelstatusApp', ['ngResource']);

modelstatusApp.factory('ModelRun', ['$resource',
    function($resource) {
        return $resource('/modelstatus/v0/model_run/:id');
    }]
);

modelstatusApp.controller('ModelRunCtrl', ['$scope', 'ModelRun', function($scope, ModelRun) {

    $scope.now = new Date();
    $scope.filter = {};
    $scope.filter.id = '';
    $scope.filter.data_provider = '';
    $scope.filter.reference_time = '';
    $scope.limit = 20;
    $scope.model_runs = [];

    $scope.refresh = function() {
        if ($scope.filter.id) {
            $scope.model_runs = [ModelRun.get({'id': $scope.filter.id})];
        } else {
            $scope.model_runs = ModelRun.query({
                'limit': $scope.limit,
                'data_provider': $scope.filter.data_provider,
                'reference_time': $scope.filter.reference_time
            });
        }
        $scope.now = new Date();
    };

    $scope.$watch('limit', $scope.refresh);
    $scope.$watchCollection('filter', $scope.refresh);

}]);
