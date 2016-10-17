$( "#new-game" ).submit(function( event ) {
  event.preventDefault();

  $.post( "/api/games/", function( data ) {
    window.location.href = "/games/" + data.key;
  });
});
