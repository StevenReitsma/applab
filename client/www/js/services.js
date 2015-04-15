angular.module('starter.services', ['ngResource'])

.factory('Login', function($resource, config) {
	return $resource(config.backend + '/api/users/login');
})

.factory('Achievement', function($resource, config) {
	return $resource(config.backend + '/api/achievements');
});