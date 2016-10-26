var apiPlayers = "/api/games/" + key + "/players/";

$(function() {

  $.get( apiPlayers, function(data) {
    var total = data.length;
    var remaining = "?";
    var message = "Waiting for " + remaining + " of " + total + " players to finish their turns."
    $("#players-pending").text(message);
  });

});


$("#finish-turn").submit(function(event) {

  event.preventDefault();

  alert("TBD");

});
