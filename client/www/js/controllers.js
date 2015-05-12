angular.module('starter.controllers', [])

.controller('AchievementsCtrl', function($scope, Login, Achievement) {
	$scope.achieved = Achievement.query({achieved: true});
	$scope.progress = Achievement.query({achieved: false, progress: true});
	$scope.other = Achievement.query({achieved: false, progress: false});
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
			
			// We are now logged in, go to dashboard
			$state.go('app.dashboard');
		}, function(error) {
			// Error
			$scope.errorMessage = "Wrong username or password";
		});
	};
});