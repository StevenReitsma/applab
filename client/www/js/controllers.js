angular.module('starter.controllers', [])

.controller('AchievementsCtrl', function($scope, Login, Achievement) {
	// Set loading
	$scope.achievements = [{"name": "Loading..."}];

	var login = new Login({"email": "steven@properchaos.nl", "password": "test"});
	login.$save().catch(function(response) {
		// Error
		$scope.error = true;
		alert("Wrong username or password.");
		alert(JSON.stringify(response));
	}).then(function() {
		if (!$scope.error)
		{
			var tokenId = login.id;
			// We are now logged in, get achievements
			$scope.achievements = Achievement.query();
		}
	});


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