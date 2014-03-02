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


pptwitter.badges = [{
    badge: 'Ace of Onomatopoeia',
    description: 'Onomatopoeia: use of word(s) that imitate the sound it denotes.',
    threshold: 0
},{
    badge: 'Master of Oxymoron',
    description: 'Oxymoron: a short phrase that appears self-contradictory. i.e wise fool, old child, black light, et cetera. Love them.',
    threshold: 500
},{
    badge: 'Prince of Hyperbole',
    description: 'Hyperbole: A bold, deliberate overstatement, e.g., "I\'d give my right arm for a slice of pizza" Not intended to be taken literally it is used as a means of emphasizing the truth of a statement.',
    threshold: 4000
},{
    badge: 'King of Simile',
    description: 'Simile: a comparison using “like” or “as," e.g. you are as beautiful as a rose.',
    threshold: 10000
},{
    badge: 'Emperor of Metaphor',
    description: 'Metaphor: a comparison not using like or as when one thing is said to be another.',
    threshold: 50000
}];
