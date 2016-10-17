var urlGame = "/api/games/" + key;
var urlPlayers = urlGame + "/players/"
var urlPlayer = null;

$( "#join-game" ).submit(function( event ) {
  event.preventDefault();

  var data = { "code": $( "#code" ).val() };
  $.post( urlPlayers, data, function( data ) {
    urlPlayer = data.uri;
    alert("You have joined as the " + data.color + " player." +
          "\n\n" + "Remember your secret code: " + data.code);

    window.location.href = "/games/" + key;
  });
});
