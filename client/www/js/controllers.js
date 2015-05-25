angular.module('starter.controllers', [])

.controller('AchievementsCtrl', function($scope, AchievementAchieved, AchievementProgress, AchievementOther, Watchlist) {
	$scope.achieved = AchievementAchieved.query();
	$scope.progress = AchievementProgress.query();
	$scope.other = AchievementOther.query();

	$scope.addToWatchlist = function(id, index, source)
	{
		// Create new watchlist item
		var item = new Watchlist({"aid": id});
		item.$save();

		if (source == 'progress')
		{
			$scope.progress[index].watchlisted = true
		}
		else if (source == 'other')
		{
			$scope.other[index].watchlisted = true
		}
	};

	$scope.removeFromWatchlist = function(id, index, source)
	{
		Watchlist.delete({"aid": id})

		if (source == 'progress')
		{
			$scope.progress[index].watchlisted = false
		}
		else if (source == 'other')
		{
			$scope.other[index].watchlisted = false
		}
	};
})

.controller('WatchlistCtrl', function($scope, $state, Watchlist) {
	$scope.watchlist = Watchlist.query();

	$scope.removeFromWatchlist = function(id, index)
	{
		Watchlist.delete({"aid": id})

		$scope.watchlist.splice(index, 1);
	};

	$scope.goToAchievements = function()
	{
		$state.go('app.achievements')
	}
})

.controller('StartupRouterCtrl', function($scope, $state, Token) {
	function isValidToken()
	{
		response = Token.get();
		return response;
	};

	// If we are logged in, and our token is valid, jump to dashboard
	if (window.localStorage['loggedin'] && isValidToken())
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
			window.localStorage['token'] = login.token;
			
			// We are now logged in, go to dashboard
			$state.go('app.dashboard');
		}, function(error) {
			// Error
			$scope.errorMessage = "Wrong username or password";
		});
	};
})

.controller('ProfileCtrl', function($scope, UserProfile) {
	$scope.profile = UserProfile.get();
})

.controller('AddFriendCtrl', function($scope, $state,Friends,NonFriends){
	$scope.addfriend = function(name){
		var item = new Friends({"name":name})
		item.$save();
		$state.go('app.friends');
		$scope.list = Friends.query()
	
	}
	$scope.users = NonFriends.query()	
})

.controller('FriendsCtrl', function($scope, $state,Friends) {
	$scope.friends = Friends.query();
	$scope.addfriends = function(){
		$state.go('app.addfriends');
	}

	$scope.removefriend = function(names,index){
		Friends.delete({"names":names})
		$scope.friends.splice(index, 1);
	}
})

.controller('RankingCtrl', function($scope, Ranking) {
	$scope.ranking = Ranking.query();
})

.controller('DashboardCtrl', function($scope, Dashboard) {
	$scope.round_to_5 = function(x)
	{
		return Math.floor(5 * Math.round(x / 5))
	};

	var dash = Dashboard.get();
	$scope.dash = dash
});
