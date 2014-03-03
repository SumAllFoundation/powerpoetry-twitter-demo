'use strict';


pptwitter.config(['$routeProvider', function($routeProvider) {
    console.log('Setting up routes...');
    $routeProvider.
        when('/', {redirectTo: '/poetic/latest/0'}).
        when('/poet/:poet', {
            templateUrl: 'static/partials/poet.html',
            controller: 'PoetCtrl',
            resolve: {
                tweets: pptwitter.apiResolver('tweet/', function(params) {
                    return {
                        ordering: '-score',
                        tweeted_by: params.poet
                    };
                }),
                score: pptwitter.apiResolver(function(params) {
                    return 'tweet/score/' + params.poet;
                }, {})
            }
        }).
        when('/poetic/:slice/:tweet', {
            templateUrl: 'static/partials/poetic.html',
            controller: 'PoeticCtrl',
            resolve: {
                data: pptwitter.apiResolver(
                    function(params) {
                        if (params.slice == 'leaders') {
                            return 'tweet/score/';
                        }
                        if (params.slice == 'greatest') {
                            return 'tweet/rating/';

                        }
                        if (params.slice == 'latest') {
                            return 'tweet/';
                        }
                    },
                    function(params) {
                        if (params.slice == 'leaders') {
                            return {};
                        }
                        if (params.slice == 'greatest') {
                            return {ordering: '-score'};

                        }
                        if (params.slice == 'latest') {
                            return {ordering: '-id'};
                        }
                    }
                ),
                tweet: function($injector, $route) {
                    var tweet = parseInt($route.current.params.tweet);
                    if (tweet) {
                        return pptwitter.apiResolver('tweet/' + tweet)($injector, $route);
                    }

                    return pptwitter.apiResolver('tweet/', {
                        ordering: '-id',
                        limit: 1
                    })($injector, $route);
                }
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


pptwitter.controller('PoeticCtrl', function($http, $route, $routeParams, $scope, $timeout, tweet, data, Data) {
    console.log('Loading PoeticCtrl...');
    $scope.Data = Data;
    $scope.tweet = parseInt($routeParams.tweet) ? tweet : tweet.objects[0];

    $scope.Data.isPhone = $(window).width() < 768;
    $(window).resize(function() {
        $scope.Data.isPhone = $(window).width() < 768;
        $scope.$apply();
    });

    if ($routeParams.slice == 'leaders') {
        $scope.users = data.objects;
    } else {
        $scope.tweets = data.objects;
    }

    $scope.slice = $routeParams.slice;
    $scope.busy = false;
    $scope.badges = angular.copy(pptwitter.badges);

    $scope.selectBadge = function(badge) {
        if ($scope.selectedBadge) {
            $scope.selectedBadge.selected = false;
        }
        $scope.selectedBadge = badge;
        badge.selected = true;
    };

    $scope.selectBadge($scope.badges[0]);

    if ($routeParams.slice == 'leaders') {
        return;
    }

    var nextUrl = data.meta.next;
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

    if ($routeParams.slice != 'latest') {
        return;
    }

    $timeout(function() {
        console.log('Fetching more tweets');
        var params = {
            ordering: '-id'
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




pptwitter.controller('PoetCtrl', function($http, $route, $routeParams, $scope, tweets, score, Data) {
    console.log('Loading PoeticCtrl...');
    $scope.Data = Data;
    $scope.tweets = tweets.objects;
    $scope.poet = $routeParams.poet;
    $scope.score = score;

    angular.forEach(pptwitter.badges, function(obj, index) {
        obj.index = index;
        if (score.score >= obj.threshold) {
            $scope.badge = obj;
        }
    });

    $scope.toNextLevel = 0;
    if ($scope.badge.index + 1 < pptwitter.badges.length) {
        $scope.nextBadge = pptwitter.badges[$scope.badge.index + 1];
        $scope.toNextLevel = $scope.nextBadge.threshold - $scope.score.score;
        $scope.maxProgress = $scope.nextBadge.threshold - $scope.badge.threshold;
        $scope.progress = $scope.score.score - $scope.badge.threshold;
    }
});
