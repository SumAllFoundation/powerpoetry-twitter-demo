'use strict';


pptwitter.createApiPromise = function($rootScope, $q, url, params, settings) {
    var defer = $q.defer();
    var reqUrl = url instanceof Function ? url(settings) : url;
    var apiParams = params instanceof Function ? params(settings) : params;

    // TODO(ram): Make $http emulate $.ajax traditional mode.
    $.ajax({
        url: '/api/' + reqUrl,
        method: 'GET',
        data: apiParams || {},
        traditional: true,
        success: function(data) {
            console.log('Data loaded', data);
            defer.resolve(data);
            $rootScope.$apply();
        },
        error: function(data) {
            console.log('Error loading data.', data);
            defer.reject('Error loading data.', data);
            $rootScope.$apply();
        }
    });

    return defer.promise;
};


pptwitter.apiResolver = function(url, params) {
    return function($injector, $route) {
        var settings = $route.current.params;
        return $injector.invoke(pptwitter.createApiPromise, pptwitter, {
            url: url,
            params: params,
            settings: settings
        });
    };
};
