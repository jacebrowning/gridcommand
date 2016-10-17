var playersAPI = "/api/games/" + key + "/players/"

$( "#add-players" ).submit(function( event ) {
  event.preventDefault();

  window.location.href = "/games/" + key + "/join";
});

$(function() {
  $.get( playersAPI, function( data ) {
    var count = data.length;
    var message = count + " " + (count == 1 ? "player has" : "players have") +
      " " + "joined the game.";
    $( "#players-count" ).text(message);
  });
});
