angular.module('starter.controllers', [])

.controller('AchievementsCtrl', function($scope) {
  $scope.achievements = [
    { title: 'Test', id: 1 },
    { title: 'Test2', id: 2 },
    { title: 'Test3', id: 3 },
    { title: 'Test4', id: 4 },
    { title: 'Test5', id: 5 },
    { title: 'Test6', id: 6 }
  ];
})