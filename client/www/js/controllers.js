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