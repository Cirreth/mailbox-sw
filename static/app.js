(function() {

var app = angular.module('doorbell', []);

app.controller('MainController', function($scope, $http) {

    var beepStates = ['off', 'auto', 'on'];

    $scope.state = {
        newMail: null,
        beep: null,
        beepTimes: [null, null, null, null],
        beepTimesModels: {from1: null, to1: null, from2: null, to2: null}
    }

    $scope.reloadState = function() {
        $http.get('/state').then(
            function(result) {
                $scope.state.beep = result.data.beep;
                $scope.state.beepTimes = result.data.beepTimes;
                $scope.state.newMail = result.data.newMail;
                if ($scope.state.beep === 'auto') {
                    $scope.restoreTimesModels();
                }
            },
            function(err) {
                console.log(err);
            }
        );
    }

    $scope.switchBeep = function(newBeep) {
        $scope.state.beep = newBeep;
        $scope.sendState();
    }

    $scope.restoreTimesModels = function() {
        var bts = $scope.state.beepTimes;
        var btms = $scope.state.beepTimesModels;
        if (bts[0] && bts[1]) {
            var parts0 = bts[0].split(':');
            btms.from1 = new Date(0); btms.from1.setHours(parts0[0]); btms.from1.setMinutes(parts0[1]);
            var parts1 = bts[1].split(':');
            btms.to1 = new Date(0); btms.to1.setHours(parts1[0]); btms.to1.setMinutes(parts1[1]);
        }
        if (bts[2] && bts[3]) {
            var parts2 = bts[2].split(':');
            btms.from2 = new Date(0); btms.from2.setHours(parts2[0]); btms.from2.setMinutes(parts2[1]);
            var parts3 = bts[3].split(':');
            btms.to2 = new Date(0); btms.to2.setHours(parts3[0]); btms.to2.setMinutes(parts3[1]);
        }
    }

    $scope.onChangeTimes = function() {
        var beepTimes = [
            $scope.state.beepTimesModels.from1,
            $scope.state.beepTimesModels.to1,
            $scope.state.beepTimesModels.from2,
            $scope.state.beepTimesModels.to2
        ].map(function(item) {
            if (!item) { return; }
            var hours = '0'+item.getHours();
            var minutes = '0'+item.getMinutes();
            return hours.slice(hours.length-2, hours.length) + ':' + minutes.slice(minutes.length-2, minutes.length);
        });
        var needSend = false;
        if (beepTimes[0] && beepTimes[1]) {
            $scope.state.beepTimes[0] = beepTimes[0];
            $scope.state.beepTimes[1] = beepTimes[1];
            needSend = true;
        } else {
            $scope.state.beepTimes[0] = null;
            $scope.state.beepTimes[1] = null;
        }
        if (beepTimes[2] && beepTimes[3]) {
            $scope.state.beepTimes[2] = beepTimes[2];
            $scope.state.beepTimes[3] = beepTimes[3];
            needSend = true;
        } else {
            $scope.state.beepTimes[2] = null;
            $scope.state.beepTimes[3] = null;
        }
        if (needSend) {
            $scope.sendState();
        }
    }

    $scope.sendState = function() {
        $http.post('/state', {
            beep: $scope.state.beep,
            beepTimes: $scope.state.beepTimes
        })
        .then(
            function(result) {

            },
            function(err) {
                console.log(err);
            }
        );
    }

    $scope.unlockRequested = false;

    $scope.confirmOpen = function() {
        $http.get('/unlock')
        .then(
            function(result) {
                var data = result.data;
                $scope.unlockRequested = false;
            },
            function(err) {
                $scope.unlockRequested = false;
                console.log(err);
            }
        );
    }

    $scope.cancelOpen = function() {
        $scope.unlockRequested = false;
    }

    $scope.init = function() {
        $scope.reloadState();
    }

});

})();