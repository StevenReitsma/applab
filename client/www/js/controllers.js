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

.controller('AchievementsOtherCtrl', function($scope, $stateParams, AchievementOtherAchieved) {
	$scope.achieved = AchievementOtherAchieved.query({'name':$stateParams.name});
	$scope.progress = []
	$scope.other = []
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

.controller('ProfileCtrl', function($scope, $state, UserProfile) {
	$scope.profile = UserProfile.get();
	$scope.trueProfile = function(){
		return true;
	}

	$scope.goToAchievements = function()
	{
		$state.go('app.achievements')
	};
})

.controller('OtherProfileCtrl', function($scope, $state, $stateParams, Friend){
	$scope.profile = Friend.get({'name':$stateParams.name})
	$scope.trueProfile = function(){
		return false;
	};

	$scope.goToAchievements = function()
	{
		$state.go('app.achievements_other', {'name':$stateParams.name})
	};
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

.controller('UpdateAchievementsCtrl', function($scope, $state,UpdateAchievements) {
	$scope.update = function(activity,speed,count){
		var item = new UpdateAchievements({"activity":activity,"speed":speed,"count":count})
		item.$save()
	}
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
	
	$scope.goToFriend = function(name){
		$state.go('app.friend', {'name':name})
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
})

.controller('ActivityCtrl', function($scope, Dashboard) {
	$scope.active = false;
	$scope.currentActivity = "cycling";
	$scope.measurement = "12.8 km";
	$scope.activityType = "running";

	$scope.startActivity = function(activityType)
	{
		// Send message to server that we're currently doing an activity


		if (activityType == "running" || activityType == "cycling")
		{
			// Start distance tracking
		}
		else
		{
			// Start count tracking
		}

		// Setup a timer that periodically sends data to server and 
	};
});
