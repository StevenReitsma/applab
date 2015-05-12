angular.module('starter.services', ['ngResource'])

.factory('Login', function($resource, config) {
	return $resource(config.backend + '/api/users/login');
})

.factory('Achievement', function($resource, config) {
	return $resource(config.backend + '/api/achievements');
})

.factory('Watchlist', function($resource, config) {
	return $resource(config.backend + '/api/watchlist');
})

.factory('Token', function($resource, config) {
	return $resource(config.backend + '/api/users/existsToken?token=:token', {token:'@token'});
});
