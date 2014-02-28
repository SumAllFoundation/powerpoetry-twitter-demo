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
