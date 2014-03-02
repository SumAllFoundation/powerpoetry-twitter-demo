pptwitter.directive('whenScrolled', function() {
    return {
        scope: {
            busy: '=',
            whenScrolled: '='
        },
        link: function(scope, elm, attr) {
            var raw = elm[0];
            elm.bind('scroll', function() {
                if (raw.scrollTop + raw.offsetHeight >= raw.scrollHeight && !scope.busy) {
                    scope.whenScrolled();
                }
            });
        }
    };
});


pptwitter.directive('raty', function($http) {
    return  {
        scope: {
            tweet: '='
        },
        template: (
            '<div rating max="3" class="rating" ng-class="{rated: tweet.user_rating}" ' +
            '    ng-click="rate()" value="score" readonly="tweet.user_rating" ' +
            '    on-hover="hover(value)" on-leave="hover(null)"></div>'
        ),
        link: function(scope, elm, attrs) {
            scope.score = scope.tweet.user_rating || scope.tweet.rating;
            scope.hover = function(value) {
                if (scope.tweet.user_rating) {
                    return;
                }

                if (value) {
                    elm.find('> span').addClass('rating-hover');
                } else {
                    elm.find('> span').removeClass('rating-hover');
                }
            };

            scope.rate = function() {
                if (scope.tweet.user_rating) {
                    return;
                }

                $http({
                    url: '/api/rating/',
                    method: 'POST',
                    data: {tweet: scope.tweet.id, rating: scope.score}
                }).success(function(data, status, headers, config) {
                    console.log('Tweet successfully rated.');
                    scope.tweet.user_rating = data.rating;
                    scope.tweet.rating = data.tweet.rating;
                    scope.tweet.rate_count = data.tweet.rate_count;
                }).error(function(data, status, headers, config) {
                    console.log('Unable to rate tweet.');
                });
            };
        }
    };
});
