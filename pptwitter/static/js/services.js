'use strict';


pptwitter.factory('Data', function($http, $location, $modal, $rootScope, $timeout) {
    return {
        user: window.user,
        go: function(path) {
            $location.path(path);
        },
        setLocation: function(url) {
            window.location = url;
        },
        flash: function(message, level) {
            this.message = message;
            this.level = level || 'danger';
        },
        confirm: function(message, callback) {
            var callbackArgs = Array.prototype.slice.apply(arguments).splice(2);
            var scope = $rootScope.$new();
            scope.message = message || 'Are you sure you want to perform this action?';

            $modal.open({
                templateUrl: 'confirmDialog.html',
                backdropFade: true,
                dialogFade:true,
                scope: scope
            }).result.then(function(result) {
                result && callback.apply(null, callbackArgs);
            });
        }
    };
});
