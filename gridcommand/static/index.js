var apiGamesIndex = "/api/games/";


$("#new-game").submit(function(event) {

  event.preventDefault();

  $.post(apiGamesIndex, function(data) {
    window.location.href = "/games/" + data.key;
  });

});
