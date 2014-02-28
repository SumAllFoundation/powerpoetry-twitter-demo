'use strict';


pptwitter.config(['$routeProvider', function($routeProvider) {
    console.log('Setting up routes...');
    $routeProvider.
        when('/', {redirectTo: '/poetic/latest/1'}).
        when('/poet/:poet', {
            templateUrl: 'static/partials/poet.html',
            controller: 'PoetCtrl',
            resolve: {
                tweets: pptwitter.apiResolver('tweet/', function(params) {
                    return {
                        ordering: '-score',
                        tweeted_by: params.poet
                    };
                })
            }
        }).
        when('/poetic/:slice/:tweet', {
            templateUrl: 'static/partials/poetic.html',
            controller: 'PoeticCtrl',
            resolve: {
                tweets: pptwitter.apiResolver('tweet/', function(params) {
                    return {
                        ordering: params.slice == 'greatest' ? '-score' : '-created_at'
                    };
                }),
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


pptwitter.controller('PoeticCtrl', function($http, $route, $routeParams, $scope, $timeout, tweets, tweet, Data) {
    console.log('Loading PoeticCtrl...');
    $scope.Data = Data;
    $scope.tweet = tweet;
    $scope.tweets = tweets.objects;
    $scope.slice = $routeParams.slice;
    $scope.busy = false;

    var nextUrl = tweets.meta.next;
    $scope.nextPage = function() {
        console.log('Requesting tweets...');
        $scope.busy = true;
        var url = nextUrl;
        if ($routeParams.slice == 'latest') {
            var lastId = $scope.tweets[$scope.tweets.length - 1].id;
            url = '/api/tweet/?ordering=-created_at&id__lt=' + lastId;
        }

        if (!url) {
            return;
        }

        $http({
            url: url,
            method: 'GET',
        }).success(function(data, status, headers, config) {
            console.log('Received ' + data.objects.length + ' new tweets.');
            $scope.tweets.push.apply($scope.tweets, data.objects);
            console.log('Showing ' + $scope.tweets.length + ' tweets.');
            nextUrl = data.meta.next;
            $scope.busy = false;
        }).error(function(data, status, headers, config) {
            console.log('Error fetching tweets.');
            $scope.busy = false;
        });
    };

    if ($routeParams.slice == 'greatest') {
        return;
    }

    $timeout(function() {
        console.log('Fetching more tweets');
        var params = {
            ordering: '-created_at'
        };

        if ($scope.tweets.length) {
            params.id__gt = $scope.tweets[0].id;
        }

        $scope.busy = true;
        $http({
            url: '/api/tweet/',
            method: 'GET',
            params: params
        }).success(function(data, status, headers, config) {
            console.log('Received ' + data.objects.length + ' new tweets.');
            $scope.busy = false;
            if ($routeParams.slice == 'greatest') {
                $scope.tweets = data.objects;
                return;
            }

            data.objects.reverse();
            angular.forEach(data.objects, function(t) {
                $scope.tweets.unshift(t);
            });
        }).error(function(data, status, headers, config) {
            console.log('Error fetching tweets.');
            $scope.busy = false;
        });
    }, 8000);
});




pptwitter.controller('PoetCtrl', function($http, $route, $routeParams, $scope, tweets, Data) {
    console.log('Loading PoeticCtrl...');
    $scope.Data = Data;
    $scope.tweets = tweets.objects;
    $scope.poet = $routeParams.poet;
});
