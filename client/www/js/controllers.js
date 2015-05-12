angular.module('starter.controllers', [])

.controller('AchievementsCtrl', function($scope, Achievement, Watchlist) {
	$scope.achieved = Achievement.query({achieved: true});
	$scope.progress = Achievement.query({achieved: false, progress: true});
	$scope.other = Achievement.query({achieved: false, progress: false});

	$scope.addToWatchlist = function(id)
	{
		// Create new watchlist item
		var item = new Watchlist({userId: window.localStorage['userid'], achievementId: id});
		item.$save();
	};

	$scope.removeFromWatchlist = function(id)
	{
		var item = Watchlist.get({userId: window.localStorage['userid'], achievementId: id});
		item.$delete();
	};
})

.controller('WatchlistCtrl', function($scope, Watchlist) {
	$scope.watchlist = Watchlist.query();
})

.controller('StartupRouterCtrl', function($scope, $state, Token) {
	function isValidToken(token)
	{
		response = Token.get({"token": token});
		return response.response;
	};

	// If we are logged in, and our token is valid, jump to dashboard
	if (window.localStorage['loggedin'] && isValidToken(window.localStorage['token']))
	{
		$state.go('app.dashboard');
	}
	// Else, jump to login screen
	else
	{
		// Remove existing tokens
		window.localStorage['loggedin'] = false;
		window.localStorage['token'] = "";

		$state.go('login');
	}
})

.controller('LoginCtrl', function($scope, $state, Login) {
	$scope.login = function(user) {
		// Do login
		var login = new Login(user);
		login.$save().then(function() {
			// Set local storage
			window.localStorage['loggedin'] = true;
			window.localStorage['token'] = login.id;
			window.localStorage['userid'] = login.userId;
			
			// We are now logged in, go to dashboard
			$state.go('app.dashboard');
		}, function(error) {
			// Error
			$scope.errorMessage = "Wrong username or password";
		});
	};
});