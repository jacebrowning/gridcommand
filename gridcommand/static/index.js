$( "#new-game" ).submit(function( event ) {
  event.preventDefault();

  $.post( "api/games/", function( data ) {
    console.log(data);
    var key = data.uri.split("/").pop()
    window.location.href = "games/" + key;
  });
});
