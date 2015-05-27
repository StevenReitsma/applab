// Ionic Starter App

// angular.module is a global place for creating, registering and retrieving Angular modules
// 'starter' is the name of this angular module example (also set in a <body> attribute in index.html)
// the 2nd parameter is an array of 'requires'
// 'starter.controllers' is found in controllers.js
angular.module('starter', ['ionic', 'starter.config', 'starter.services', 'starter.controllers'])

.run(function($ionicPlatform) {
  $ionicPlatform.ready(function() {
    // Hide the accessory bar by default (remove this to show the accessory bar above the keyboard
    // for form inputs)
    if (window.cordova && window.cordova.plugins.Keyboard) {
      cordova.plugins.Keyboard.hideKeyboardAccessoryBar(true);
    }
    if (window.StatusBar) {
      // org.apache.cordova.statusbar required
      StatusBar.styleDefault();
    }
  });
})

.config(function($stateProvider, $urlRouterProvider) {
  $stateProvider

  .state('startupRouter', {
    url: "/",
    controller: 'StartupRouterCtrl'
  })
  .state('app', {
    url: "/app",
    abstract: true,
    templateUrl: "templates/menu.html"
  })
  .state('login', {
    url: "/login",
    templateUrl: "templates/login.html",
    controller: "LoginCtrl"
  })
  .state('app.dashboard', {
    url: "/dashboard",
    views: {
      'menuContent': {
        templateUrl: "templates/dashboard.html",
        controller: "DashboardCtrl"
      }
    }
  })

  .state('app.achievements', {
    url: "/achievements",
    views: {
      'menuContent': {
        templateUrl: "templates/achievements.html",
        controller: 'AchievementsCtrl'
      }
    }
  })
    .state('app.watchlist', {
      url: "/watchlist",
      cache: false,
      views: {
        'menuContent': {
          templateUrl: "templates/watchlist.html",
          controller: 'WatchlistCtrl'
        }
      }
    })

  .state('app.profile', {
    url: "/profile",
    views: {
      'menuContent': {
        templateUrl: "templates/profile.html",
		controller: 'ProfileCtrl'
		
      }
    }
  })
  .state('app.ranking', {
    url: "/ranking",
    views: {
      'menuContent': {
        templateUrl: "templates/ranking.html",
		controller: 'RankingCtrl'
      }
    }
  })
    .state('app.friends', {
    url: "/friends",
	cache: false,
    views: {
      'menuContent': {
        templateUrl: "templates/friends.html",
		controller: 'FriendsCtrl'
      }
    }
  })
    .state('app.addfriends', {
    url: "friends/add",
	cache: false,
    views: {
      'menuContent': {
        templateUrl: "templates/addfriends.html",
		controller: 'AddFriendCtrl'
      }
    }
  })
    .state('app.friend', {
    url: "/users/friends/:name",
    views: {
      'menuContent': {
        templateUrl: "templates/profile.html",
		controller: 'OtherProfileCtrl'
      }
    }
  });
  // if none of the above states are matched, use this as the fallback
  $urlRouterProvider.otherwise('/');
});
