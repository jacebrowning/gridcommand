var apiGame = "/api/games/" + key;
var apiPlayers = apiGame + "/players/"
var uriPlayer = null;


$("#join-game").submit(function(event) {

  event.preventDefault();

  var code = $("#code").val();
  var data = {"code": code};
  $.post( apiPlayers, data, function(data) {
    uriPlayer = data.uri;
    alert("You have joined as the " + data.color + " player." +
          "\n\n" + "Remember your secret code: " + data.code);

    window.location.href = "/games/" + key;
  })
  .fail(function(response) {
    alert("Error: " + response.responseJSON.message);
  });

});
