angular.module('starter.services', ['ngResource'])

.factory('Login', function($resource, config) {
	return $resource(config.backend + '/login');
})

.factory('AchievementAchieved', function($resource, config) {
	return $resource(config.backend + '/achievements/unlocked?key=' + window.localStorage['token']);
})

.factory('AchievementProgress', function($resource, config) {
	return $resource(config.backend + '/achievements/progress?key=' + window.localStorage['token']);
})

.factory('AchievementOther', function($resource, config) {
	return $resource(config.backend + '/achievements/other?key=' + window.localStorage['token']);
})

.factory('Watchlist', function($resource, config) {
	return $resource(config.backend + '/users/watchlist?key=' + window.localStorage['token']);
})

.factory('Token', function($resource, config) {
	return $resource(config.backend + '/validate?key=' + window.localStorage['token']);
})

.factory('Ranking', function($resource, config) {
	return $resource(config.backend + '/ranking?key=' + window.localStorage['token']);
});
