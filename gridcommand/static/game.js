var apiPlayers = "/api/games/" + key + "/players/"
var apiStart = "/api/games/" + key + "/start"

$(function() {

  $.get( apiPlayers, function(data) {
    var count = data.length;
    var message = count + " " + (count == 1 ? "player has" : "players have") +
      " " + "joined the game.";
    $("#players-joined").text(message);
  });

});


$("#add-players").submit(function(event) {

  event.preventDefault();

  window.location.href = "/games/" + key + "/join";

});


$("#start-game").submit(function(event) {

  event.preventDefault();

  $.post(apiStart, function(data) {
    window.location.href = "/games/" + key + "/board";
  })
  .fail(function(response) {
    alert("Error: " + response.responseJSON.message);
  });

});

