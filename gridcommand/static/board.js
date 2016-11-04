var apiGame = "/api/games/" + key;
var apiPlayers = "/api/games/" + key + "/players/";

$(function() {
  var remaining = null;
  var total = null;

  $.when(

    $.get(apiGame, function(data) {
      remaining = data.pending;
    }),

    $.get(apiPlayers, function(data) {
      total = data.length;
    })

  ).done(function() {

    var message = "Waiting for " + remaining + " of " + total + " players to finish their turns.";
    $("#players-pending").text(message);

  });
});


$("#finish-turn").submit(function(event) {
  event.preventDefault();

  alert("TBD");

});
