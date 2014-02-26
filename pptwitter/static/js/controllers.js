'use strict';


pptwitter.config(['$routeProvider', function($routeProvider) {
    console.log('Setting up routes...');
    $routeProvider.
        when('/', {redirectTo: '/poetic/1'}).
        when('/poetic/:tweet', {
            templateUrl: 'static/partials/poetic.html',
            controller: 'PoeticCtrl',
            resolve: {
                tweets: pptwitter.apiResolver('tweet/', {ordering: '-created_at'}),
                tweet: pptwitter.apiResolver(function(params) {
                    return 'tweet/' + params.tweet;
                })
            }
        }).
        otherwise({
            redirectTo: '/'
        });
}]);


pptwitter.controller('AppCtrl', function($rootScope, $scope, $timeout, $location, Data) {
    console.log('Loading AppCtrl...');
    $scope.Data = Data;
    $(window).resize(function() {
        $scope.navCollapsed = $(window).width() < 768;
        $scope.$apply();
    });

    $rootScope.$on('$routeChangeStart', function(event, next, current) {
        Data.message = null;
        Data.loading = true;
        $scope['class'] = {};
        if (next.$$route) {
            $scope['class'][next.$$route.controller] = 'active';
        }
    });

    $rootScope.$on('$routeChangeSuccess', function(event, current, previous) {
        $scope.navCollapsed = true;
        Data.loading = false;
        window.scrollTo(0, 0);
    });

    $rootScope.$on('$routeChangeError', function(event, current, previous, rejection) {
        console.log(rejection);
        Data.loading = false;
        Data.flash(rejection);
    });
});


pptwitter.controller('PoeticCtrl', function($http, $route, $scope, $timeout, tweets, tweet, Data) {
    console.log('Loading PoeticCtrl...');
    $scope.Data = Data;
    $scope.tweet = tweet;
    $scope.tweets = tweets.objects;

    var score = tweet.score;
    $scope.averageScore = (score.poetic + score.sentiment + score.language) / 3.0;

    $timeout(function() {
        console.log('Fetching more tweets');
        var url = '/api/tweet?ordering=-created_at';
        if ($scope.tweets.length) {
            url += '&id__gt=' + $scope.tweets[0].id;
        }

        $http({
            url: url,
            method: 'GET'
        }).success(function(data, status, headers, config) {
            console.log('Received ' + data.objects.length + ' new tweets.');
            data.objects.reverse();
            angular.forEach(data.objects, function(t) {
                $scope.tweets.unshift(t);
            });
        }).error(function(data, status, headers, config) {
            console.log('Error fetching tweets.');
        });
    }, 10000);
});
