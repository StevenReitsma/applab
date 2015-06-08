angular.module('starter.controllers', [])

.controller('AchievementsCtrl', function($scope, AchievementAchieved, AchievementProgress, AchievementOther, Watchlist, InsertClick) {
	var click = new InsertClick({"page":"Achievements", "details":{}})
	click.$save();

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

.controller('WatchlistCtrl', function($scope, $state, Watchlist, InsertClick) {
	
	var click = new InsertClick({"page":"Watchlist", "details":{}})
	click.$save();

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
	Token.get({}, function(response, headers) {
		if (response.valid === true && window.localStorage['loggedin'])
		{
			$state.go('app.dashboard');
		}
		else
		{
			// Remove existing tokens
			window.localStorage['loggedin'] = false;
			window.localStorage['token'] = "";

			$state.go('login');
		}
	});
})

.controller('LoginCtrl', function($scope, $state, Login, Token) {
	Token.get({}, function(response, headers) {
		if (response.valid === true && window.localStorage['loggedin'])
		{
			$state.go('app.dashboard');
		}
	});

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

.controller('ProfileCtrl', function($scope, $state, UserProfile, InsertClick) {
	var click = new InsertClick({"page":"Ownprofile", "details":{}})
	click.$save();

	$scope.profile = UserProfile.get();
	$scope.trueProfile = function(){
		return true;
	}
	
	$scope.anonymous = function(anon){
		var item = new UserProfile({"anonymous":anon})
		item.$save();
	}
	
	$scope.goToAchievements = function()
	{
		$state.go('app.achievements')
	};
})

.controller('OtherProfileCtrl', function($scope, $state, $stateParams, Friend, InsertClick){
	var click = new InsertClick({"page":"Oherprofile", "details":{"friend":$stateParams.name}})
	click.$save();

	$scope.profile = Friend.get({'name':$stateParams.name})
	$scope.trueProfile = function(){
		return false;
	};

	$scope.goToAchievements = function()
	{
		$state.go('app.achievements_other', {'name':$stateParams.name})
	};
})

.controller('AddFriendCtrl', function($scope, $state,Friends,NonFriends, InsertClick){
	var click = new InsertClick({"page":"AddFriend", "details":{}})
	click.$save();

	$scope.addfriend = function(name){
		var item = new Friends({"name":name})
		item.$save();
		$state.go('app.friends');
		$scope.list = Friends.query()
	
	}
	$scope.users = NonFriends.query()	
})

	
.controller('FriendsCtrl', function($scope, $state,Friends, InsertClick) {
	var click = new InsertClick({"page":"Friends", "details":{}})
	click.$save();

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

.controller('RankingCtrl', function($scope, Ranking, InsertClick) {
	var click = new InsertClick({"page":"Ranking", "details":{}})
	click.$save();

	$scope.ranking = Ranking.query();
})

.controller('DashboardCtrl', function($scope, Dashboard, InsertClick) {
	var click = new InsertClick({"page":"Dashboard", "details":{}})
	click.$save();

	$scope.round_to_5 = function(x)
	{
		if (x > 95 && x < 100)
			return 95;
		return Math.floor(5 * Math.round(x / 5))
	};

	var dash = Dashboard.get();
	$scope.dash = dash
})

.controller('ActivityCtrl', function($scope, $ionicPopup, Dashboard, UpdateAchievements, InsertClick, Tester) {
	$scope.active = false;
	$scope.currentActivity = "running";
	$scope.measurement = 0;
	var lastCall = 0;
	var bgGeo;

	var prevLat;
	var prevLon;
	var count = 0;
	var startTime = 0;

	$scope.startActivity = function(activityType)
	{
		$scope.measurement = 0
		$scope.active = true;
		$scope.currentActivity = activityType;
		startTime = Date.now();

		console.log($scope.currentActivity);

		if ($scope.currentActivity == "running" || $scope.currentActivity == "cycling")
		{
			// Active location plugins
		    navigator.geolocation.getCurrentPosition(function(location) {
		        console.log('OK');
		    });

    		bgGeo = window.plugins.backgroundGeoLocation;

		    /**
		    * This callback will be executed every time a geolocation is recorded in the background.
		    */
		    var callbackFn = function(location) {
		    	// Add distance
				calculateDifference = function(lat1, lon1, lat2, lon2)
				{
					var radlat1 = Math.PI * lat1/180
					var radlat2 = Math.PI * lat2/180
					var radlon1 = Math.PI * lon1/180
					var radlon2 = Math.PI * lon2/180
					var theta = lon1-lon2
					var radtheta = Math.PI * theta/180
					var dist = Math.sin(radlat1) * Math.sin(radlat2) + Math.cos(radlat1) * Math.cos(radlat2) * Math.cos(radtheta);
					dist = Math.acos(dist)
					dist = dist * 180/Math.PI
					dist = dist * 60 * 1.1515
					dist = dist * 1.609344
					return dist
				};

				// Add distance to measurement
				$scope.$apply(function ()
				{
					if (count > 0)
						$scope.measurement += calculateDifference(prevLat, prevLon, location.latitude, location.longitude);
					count++;
				});

				prevLat = location.latitude;
				prevLon = location.longitude;
		    };

		    var failureFn = function(error) {
		        // Error
		    };

		    // BackgroundGeoLocation is highly configurable.
		    bgGeo.configure(callbackFn, failureFn, {
		        url: 'http://athlos.properchaos.nl:5000/geotest',
		        params: {

		        },
		        headers: {

		        },
		        desiredAccuracy: 0,
		        stationaryRadius: 0,
		        distanceFilter: 0,
		        notificationTitle: 'Athlos', // <-- android only, customize the title of the notification
		        notificationText: 'Tracking active', // <-- android only, customize the text of the notification
		        debug: false, // <-- enable this hear sounds for background-geolocation life-cycle.
		        stopOnTerminate: false // <-- enable this to clear background location settings when the app terminates
		    });

		    // Turn ON the background-geolocation system.  The user will be tracked whenever they suspend the app.
		    bgGeo.start();
		}
		else
		{
			// Pushups
		}
	};

	$scope.increment = function()
	{
		var now = Date.now();
		if (lastCall + 1000 < now){
			$scope.measurement += 1;
			lastCall = now;
			$scope.warning = false;
		}
		else
		{
			$scope.warning = true;
		}
		
	};
	
	$scope.stopActivity = function()
	{
		var online = true;
		if (navigator.connection)
		{
			var networkState = navigator.connection.type;

			console.log(networkState)
			if (networkState == 'none'){
				online = false;

			}
			else{
				online = true;

			}
				
		}

		if (online === false)
		{
			// Internet offline, save for later.
			$scope.internetGone = true;
			
		}
		else
		{
			$scope.internetGone = false;

			var click = new InsertClick({"page":"Activity", "details":{"ActivityType":$scope.currentActivity,"value":$scope.measurement}});
			click.$save();

			var speed = 0;
			if ($scope.currentActivity == "running" || $scope.currentActivity == "cycling")
			{
				speed = $scope.measurement / (Date.now() - startTime) * 1000 * 60 * 60;
			}

			var item = new UpdateAchievements({"activity":$scope.currentActivity,"speed":speed,"count":$scope.measurement});

			item.$save($scope.popup);
			

			$scope.active = false;
			
			bgGeo.finish();
		}
	};

	$scope.popup = function(achieved,headers) {
		console.log(JSON.stringify(achieved));
		var template = ""
		for (i = 0; i < achieved.unlocked.length; i++){
			if (i != achieved.unlocked.length-1){
				un = achieved.unlocked[i].concat(", ")
			}
			else {
				un = achieved.unlocked[i]
			}
			template = template.concat(un) 
		}
		if (template){
			var alertPopup = $ionicPopup.alert({
				title: 'Achievement(s) unlocked!',
				template: template
			});
		}
	};
});
